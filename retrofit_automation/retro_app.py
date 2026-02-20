import logging
from pathlib import Path

import streamlit as st
import yaml

from analysis.tag_extractor import content_has_any_tag, extract_tagged_blocks
from analysis.retrofit_applier import retrofit_file
from workspace.workspace_manager import create_retro_workspace
import styles  # Import the new styles module

# ─────────────────────────────────────
# Logging
# ─────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────
# Config loader
# ─────────────────────────────────────
def load_config() -> dict:
    config_path = Path(__file__).resolve().parent / "config" / "retrofit_config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def resolve_target_file(
    source_file: Path,
    source_root: Path,
    target_root: Path,
    folder_mapping: dict,
) -> Path | None:
    """
    Find the matching target file.
    Returns the target Path, or None if not found (→ new unit).
    """
    ext = source_file.suffix.lower()
    filename = source_file.name
    relative_path = source_file.relative_to(source_root)

    # Strategy 1: explicit folder mapping
    mapped_folder = folder_mapping.get(ext, "")
    if mapped_folder:
        candidate = target_root / mapped_folder / filename
        if candidate.exists():
            return candidate

    # Strategy 2: same relative path
    candidate = target_root / relative_path
    if candidate.exists():
        return candidate

    # Strategy 3: recursive filename search
    matches = list(target_root.rglob(filename))
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # Multiple matches — try matching by parent folder
        source_parent = source_file.parent.name.lower()
        for m in matches:
            if m.parent.name.lower() == source_parent:
                return m
        # Still ambiguous — take first match
        logger.warning(
            "Multiple target matches for '%s': %s — using first",
            filename,
            [str(m) for m in matches],
        )
        return matches[0]

    return None


# ═══════════════════════════════════
# Streamlit UI
# ═══════════════════════════════════
st.set_page_config(page_title="Retrofit Automation", layout="wide")

# Inject Custom CSS
st.markdown(styles.get_custom_css(), unsafe_allow_html=True)

st.title("🔁 Code Retrofit Automation")

# ── Visual Flowchart ──
st.markdown("### 🛠️ Process Flow")
st.graphviz_chart("""
digraph G {
    rankdir=LR;
    bgcolor="transparent";
    node [shape=box, style="filled,rounded", fillcolor="#2b2d42", fontcolor="white", fontname="Sans-Serif", color="#667eea"];
    edge [color="#a0a0a0", fontcolor="#e0e0e0", fontname="Sans-Serif"];

    Start [shape=oval, fillcolor="#667eea", color="none"];
    Mode [shape=diamond, label="Select Mode", fillcolor="#764ba2", color="none"];

    Start -> Mode;

    Scan [label="Scan Source"];
    Mode -> Scan;

    Identify [label="Identify Tagged Units"];
    Scan -> Identify;

    Exists [shape=diamond, label="Exists in Target?", fillcolor="#764ba2", color="none"];
    Identify -> Exists;

    New [label="Mark as\nNEW UNIT 🆕", fillcolor="#2b2d42"];
    Retro [label="Mark for\nRETROFIT 🔀", fillcolor="#2b2d42"];

    Exists -> New [label="No"];
    Exists -> Retro [label="Yes"];

    Action [shape=diamond, label="Mode?", fillcolor="#764ba2", color="none"];
    New -> Action;
    Retro -> Action;

    Preview [label="Show Stats Only", style="dashed,rounded"];
    Apply [label="Write files to\nRetro/ Folder", fillcolor="#10b981", color="none"];

    Action -> Preview [label="PREVIEW"];
    Action -> Apply [label="APPLY"];
}
""")

config = load_config()
SUPPORTED_EXT = set(config.get("supported_extensions", []))
FOLDER_MAPPING = config.get("folder_mapping", {})

# ── Inputs ──
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
mode = st.selectbox(
    "Select Mode",
    ["PREVIEW", "APPLY"],
    help="PREVIEW: Analyze files and show stats only (Read-Only). APPLY: Write retrofitted files to the Retro folder."
)

if mode == "PREVIEW":
    st.info("ℹ️ **PREVIEW MODE**: No files will be written. Simulation only.")
else:
    st.warning("⚠️ **APPLY MODE**: Retrofitted files will be written to the `Retro/` folder.")

reference_name = st.text_input(
    "Reference Name (workspace folder name)",
    placeholder="BANKING-123456",
)

col1, col2 = st.columns(2)
with col1:
    source_path = st.text_input(
        "Source Path (SIT)",
        placeholder="C:/Git/SIT/dev_flex1",
    )
with col2:
    target_path = st.text_input(
        "Target Path (UAT)",
        placeholder="C:/Git/UAT/cee_19c_cit",
    )

search_tags_raw = st.text_area(
    "Search Tags (semicolon-separated)",
    placeholder="BANKING-123456; BANKING-121212",
    height=100
)

btn_label = "🚀 Run Preview" if mode == "PREVIEW" else "🚀 Apply Retrofit"
start_btn = st.button(btn_label)
st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════
# Main flow
# ═══════════════════════════════════
if start_btn:

    # ── Validate inputs ──
    if not reference_name or not source_path or not target_path or not search_tags_raw:
        st.error("All inputs are mandatory.")
        st.stop()

    SOURCE_ROOT = Path(source_path.strip())
    TARGET_ROOT = Path(target_path.strip())

    if not SOURCE_ROOT.exists() or not SOURCE_ROOT.is_dir():
        st.error(f"Source path does not exist or is not a directory: `{SOURCE_ROOT}`")
        st.stop()

    if not TARGET_ROOT.exists() or not TARGET_ROOT.is_dir():
        st.error(f"Target path does not exist or is not a directory: `{TARGET_ROOT}`")
        st.stop()

    # Parse search tags
    search_tags = [t.strip() for t in search_tags_raw.split(";") if t.strip()]
    if not search_tags:
        st.error("At least one search tag is required.")
        st.stop()

    # ── Create workspace (folder structure only) ──
    workspace = create_retro_workspace(reference_name)
    SOURCE_COPY_DIR = workspace["source"]
    TARGET_COPY_DIR = workspace["target"]
    RETRO_DIR = workspace["retro"]

    # ── Scan source ──
    source_files = [
        p for p in SOURCE_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXT
    ]

    if not source_files:
        st.warning("No supported files found in source path.")
        st.stop()

    # ── Process each file ──
    results = []
    progress = st.progress(0, text="Scanning source files…")

    for idx, src_file in enumerate(source_files):
        progress.progress(
            (idx + 1) / len(source_files),
            text=f"Processing {src_file.name} ({idx+1}/{len(source_files)})",
        )

        src_content = src_file.read_text(errors="ignore")

        # Skip files that don't contain any search tag
        if not content_has_any_tag(src_content, search_tags):
            continue

        relative_path = src_file.relative_to(SOURCE_ROOT)
        
        # Determine retro output path
        retro_path = RETRO_DIR / relative_path

        # Find matching target file
        target_file = resolve_target_file(
            src_file, SOURCE_ROOT, TARGET_ROOT, FOLDER_MAPPING,
        )

        target_content = None
        if target_file is not None:
            target_content = target_file.read_text(errors="ignore")

        # ── EXECUTE: PREVIEW vs APPLY ──
        if mode == "PREVIEW":
            # Simulation: calculate what WOULD happen
            if target_file is None:
                # New unit
                result = {
                    "retrofit_type": "NEW_UNIT",
                    "blocks_found": 0,
                    "retro_path": retro_path
                }
            else:
                # Merged unit: extract blocks to count them
                blocks = extract_tagged_blocks(src_content, search_tags)
                result = {
                    "retrofit_type": "MERGED" if blocks else "SKIPPED",
                    "blocks_found": len(blocks),
                    "retro_path": retro_path
                }

        elif mode == "APPLY":
            # Write mode: Copy source/target to workspace for review comparison
            src_copy = SOURCE_COPY_DIR / relative_path
            src_copy.parent.mkdir(parents=True, exist_ok=True)
            src_copy.write_text(src_content, errors="ignore")

            if target_file:
                tgt_relative = target_file.relative_to(TARGET_ROOT)
                tgt_copy = TARGET_COPY_DIR / tgt_relative
                tgt_copy.parent.mkdir(parents=True, exist_ok=True)
                tgt_copy.write_text(target_content, errors="ignore")

            # Perform actual write
            result = retrofit_file(
                source_content=src_content,
                target_content=target_content,
                search_tags=search_tags,
                retro_file_path=retro_path,
            )

        result["source_file"] = str(relative_path)
        result["target_found"] = target_file is not None
        results.append(result)

    progress.empty()

    # ── Summary ──
    if not results:
        st.warning("No files matched the search tags in the source path.")
    else:
        st.markdown("### 📋 Retrofit Summary")

        new_units = [r for r in results if r["retrofit_type"] == "NEW_UNIT"]
        merged = [r for r in results if r["retrofit_type"] == "MERGED"]
        skipped = [r for r in results if r["retrofit_type"] == "SKIPPED"]

        col1, col2, col3 = st.columns(3)
        col1.metric("🆕 New Units", len(new_units))
        col2.metric("🔀 Merged Units", len(merged))
        col3.metric("⏭️ Skipped", len(skipped))

        st.markdown("---")
        st.markdown("#### Detailed Breakdown")

        for r in results:
            rtype = r["retrofit_type"]
            file_name = r["source_file"]
            blocks = r.get("blocks_found", 0)

            if rtype == "NEW_UNIT":
                st.write(f"🆕 **{file_name}** — New Unit (Direct Copy)")
            elif rtype == "MERGED":
                st.write(f"🔀 **{file_name}** — Retrofitted ({blocks} blocks applied)")
            else:
                st.write(f"⏭️ **{file_name}** — Skipped (No valid blocks matched)")

        st.success(f"✅ Process complete — {len(results)} file(s) analyzed.")

        if mode == "APPLY":
            st.info(f"📁 Files written to: `{workspace['base']}`")
        else:
            st.info("ℹ️ **Preview Complete**: No files were written.")
