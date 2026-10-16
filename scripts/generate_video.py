"""
Automated Introductory Video & Voiceover Generator
===================================================
Generates assets/introductory_video.mp4 with synchronized voiceover:
  Scene 1: Title & Executive Introduction (₹4,200 Cr M&A Deal Overview)
  Scene 2: Kaggle Data Ingestion & SQL Target Screener (79 Columns, 448 Firms)
  Scene 3: ₹4,200 Cr M&A Engine & Year 2 EPS Accretion (+6.4% Accretion)
  Scene 4: 5 Capital Structures, Credit Covenant Check (3.08x) & LBO Cash Sweep
  Scene 5: Wall Street Deliverables (6-Tab Excel Model & Streamlit App)

Combines isolated TTS worker with FFmpeg via imageio_ffmpeg.
"""

import os
import sys
import shutil
import subprocess
import wave
import imageio_ffmpeg
import matplotlib.pyplot as plt
import matplotlib.patches as patches

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(WORKSPACE_DIR, "assets")
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch_video")
VIDEO_OUTPUT_PATH = os.path.join(ASSETS_DIR, "introductory_video.mp4")
TTS_WORKER_SCRIPT = os.path.join(WORKSPACE_DIR, "scripts", "tts_worker.py")

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


def get_wav_duration(path: str) -> float:
    with wave.open(path, "r") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        return frames / float(rate)


def render_scene1_title(out_path: str):
    """Scene 1: Executive Title & Overview Slide."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#070B14")
    ax.set_facecolor("#070B14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    box = patches.FancyBboxPatch(
        (8, 56), 84, 34,
        boxstyle="round,pad=1.0,rounding_size=2.0",
        facecolor="#0F172A",
        edgecolor="#38BDF8",
        linewidth=2.5,
    )
    ax.add_patch(box)

    ax.text(50, 81, "CROSS-BORDER M&A ACCRETION/DILUTION", fontsize=24, fontweight="bold", color="#F8FAFC", ha="center")
    ax.text(50, 74, "& LBO SYNERGY MODEL", fontsize=24, fontweight="bold", color="#38BDF8", ha="center")
    ax.text(50, 64, "Institutional Financial Engineering Platform Powered by Kaggle NYSE Fundamentals (dgawlik/nyse)", fontsize=11, color="#94A3B8", ha="center")

    badges = [
        ("₹4,200 Cr", "Deal Enterprise Value", "#38BDF8"),
        ("₹380 Cr", "5-Year Phased Synergies", "#F59E0B"),
        ("+6.4%", "Year 2 EPS Accretion", "#00E676"),
        ("18.7% IRR", "Structure #4 Optimal Hybrid", "#A855F7"),
    ]
    for i, (val, sub, col) in enumerate(badges):
        x = 9 + i * 21
        b_box = patches.FancyBboxPatch(
            (x, 22), 19, 24,
            boxstyle="round,pad=0.8,rounding_size=1.5",
            facecolor="#111C33",
            edgecolor=col,
            linewidth=2.0,
        )
        ax.add_patch(b_box)
        ax.text(x + 9.5, 36, val, fontsize=18, fontweight="bold", color=col, ha="center")
        ax.text(x + 9.5, 29, sub, fontsize=9.5, fontweight="bold", color="#E2E8F0", ha="center")

    ax.text(50, 9, "Full 6-Tab Wall Street Excel Model  •  Interactive Streamlit Deal Room  •  Automated Test Suite", fontsize=10.5, color="#64748B", ha="center")

    plt.tight_layout()
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()


def render_scene2_ingestion(out_path: str):
    """Scene 2: Kaggle Data Ingestion & SQL Target Screener."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#070B14")
    ax.set_facecolor("#070B14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 91, "STAGE 1: KAGGLE DATA INGESTION & SQL TARGET SCREENER", fontsize=20, fontweight="bold", color="#38BDF8", ha="center")
    ax.text(50, 85, "Cleans 79 Statement Variables across 448 Companies into SQLite | Window Functions Screening", fontsize=11, color="#94A3B8", ha="center")

    box1 = patches.FancyBboxPatch(
        (8, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#38BDF8",
        linewidth=2,
    )
    ax.add_patch(box1)
    ax.text(28, 71, "[1] Data Ingestion & Database Engine", fontsize=13, fontweight="bold", color="#38BDF8", ha="center")

    ing_points = [
        "Dataset: Kaggle NYSE Fundamentals (dgawlik/nyse)",
        "Coverage: 1,781 periods across 448 S&P 500 corporations",
        "79 Financial Variables Cleaned (Revenue, EBITDA, SG&A, Debt)",
        "Automated SQLite Ingestion: data/kaggle_ma_universe.db",
        "Derived Standardized Metrics: EBITDA Margin, FCF, Net Debt",
    ]
    curr_y = 62
    for p in ing_points:
        ax.text(12, curr_y, f"• {p}", fontsize=9.2, color="#E2E8F0")
        curr_y -= 8.5

    box2 = patches.FancyBboxPatch(
        (52, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#00E676",
        linewidth=2,
    )
    ax.add_patch(box2)
    ax.text(72, 71, "[2] Institutional SQL Screening Hurdles", fontsize=13, fontweight="bold", color="#00E676", ha="center")

    scr_points = [
        "Query: sql/target_screener.sql with CTEs & Window Functions",
        "Hurdle 1: EBITDA Margin > 15.0% (Core operational health)",
        "Hurdle 2: SG&A-to-Revenue > 15.0% (Overhead synergy potential)",
        "Hurdle 3: FCF Conversion > 40.0% (Deleveraging cash flow)",
        "Hurdle 4: Net Debt / EBITDA < 2.50x (Prudent leverage)",
        "Top Candidates Screened: RHT, ADBE, CTXS, AMG, TRIP",
    ]
    curr_y = 62
    for p in scr_points:
        ax.text(56, curr_y, f"• {p}", fontsize=9.2, color="#E2E8F0")
        curr_y -= 7.0

    plt.tight_layout()
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()


def render_scene3_engine(out_path: str):
    """Scene 3: ₹4,200 Cr M&A Engine & Year 2 EPS Accretion."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#070B14")
    ax.set_facecolor("#070B14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 91, "STAGE 2: ₹4,200 CR DEAL CALIBRATION & EPS ACCRETION", fontsize=20, fontweight="bold", color="#F59E0B", ha="center")
    ax.text(50, 85, "Purchase Price Allocation (Goodwill & DTL) and 5-Year Phased Synergies Realization", fontsize=11, color="#94A3B8", ha="center")

    box1 = patches.FancyBboxPatch(
        (8, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#F59E0B",
        linewidth=2,
    )
    ax.add_patch(box1)
    ax.text(28, 71, "[1] Sources & Uses and Goodwill PPA", fontsize=13, fontweight="bold", color="#F59E0B", ha="center")

    su_points = [
        "Deal Enterprise Value: ₹4,200 Cr (12.0x on ₹350 Cr EBITDA)",
        "Target Equity Purchase Price: ₹4,000 Cr",
        "Senior Loan (8.0%): ₹850 Cr | Mezzanine (11.0%): ₹350 Cr",
        "Acquirer Cash: ₹500 Cr | Stock Consideration: ₹2,500 Cr",
        "Asset Write-up: ₹600 Cr | Deferred Tax Liability (25.17%): ₹151 Cr",
        "Goodwill Created: ₹2,351 Cr | Annual Amort: ₹29.9 Cr/yr",
    ]
    curr_y = 62
    for p in su_points:
        ax.text(12, curr_y, f"• {p}", fontsize=9.2, color="#E2E8F0")
        curr_y -= 7.0

    box2 = patches.FancyBboxPatch(
        (52, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#00E676",
        linewidth=2,
    )
    ax.add_patch(box2)
    ax.text(72, 71, "[2] Year 2 EPS Accretion Waterfall", fontsize=13, fontweight="bold", color="#00E676", ha="center")

    eps_points = [
        "Acquirer Standalone EPS: ₹45.00 (Baseline on 10 Cr sh)",
        "+ Target Standalone Earnings: +₹17.36 per share",
        "+ SG&A Synergies (Y2: ₹75 Cr pretax): +₹4.49 per share",
        "- Deal Debt Financing Interest: -₹6.38 per share",
        "- Foregone Cash Interest: -₹1.20 per share",
        "- PPA Intangible Amortization: -₹2.39 per share",
        "- Share Dilution (2.5 Cr shares issued): -₹9.00 per share",
        "= Year 2 Pro-Forma EPS: ₹47.88 (+6.4% Accretion!)",
    ]
    curr_y = 62
    for p in eps_points:
        color = "#00E676" if "+6.4%" in p or "+ Target" in p or "+ SG&A" in p else ("#EF4444" if "-" in p else "#E2E8F0")
        ax.text(56, curr_y, f"• {p}", fontsize=9.0, color=color)
        curr_y -= 5.5

    plt.tight_layout()
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()


def render_scene4_lbo(out_path: str):
    """Scene 4: Capital Structures, Credit Covenant Check & Cash Sweep."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#070B14")
    ax.set_facecolor("#070B14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 91, "STAGE 3: 5 CAPITAL STRUCTURES & LBO DELEVERAGING", fontsize=20, fontweight="bold", color="#A855F7", ha="center")
    ax.text(50, 85, "Covenant Compliance (3.08x < 3.20x limit) and 5-Year LBO Project IRR Optimization", fontsize=11, color="#94A3B8", ha="center")

    box1 = patches.FancyBboxPatch(
        (8, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#A855F7",
        linewidth=2,
    )
    ax.add_patch(box1)
    ax.text(28, 71, "[1] 5 Financing Structures Evaluated", fontsize=13, fontweight="bold", color="#A855F7", ha="center")

    structs = [
        "1. 100% Stock Swap: Net Debt 0.0x | 14.2% Base IRR (PASS)",
        "2. 70/30 Debt-Equity: Net Debt 4.22x | 17.1% IRR (BREACH)",
        "3. 50/50 Balanced: Net Debt 3.37x | 16.5% IRR (BREACH)",
        "4. Optimal Hybrid: Net Debt 3.08x | 18.7% IRR (PASS!)",
        "5. 80% Aggressive LBO: Net Debt 5.51x | 22.4% IRR (BREACH)",
        "★ Structure #4 strictly complies with the 3.20x covenant!",
    ]
    curr_y = 62
    for s in structs:
        col = "#00E676" if "PASS" in s else ("#EF4444" if "BREACH" in s else "#38BDF8")
        ax.text(12, curr_y, f"• {s}", fontsize=8.8, color=col)
        curr_y -= 7.0

    box2 = patches.FancyBboxPatch(
        (52, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#38BDF8",
        linewidth=2,
    )
    ax.add_patch(box2)
    ax.text(72, 71, "[2] 5-Year FCF Cash Sweep Schedule", fontsize=13, fontweight="bold", color="#38BDF8", ha="center")

    sweep_pts = [
        "EBITDA Expansion: ₹411 Cr (Y1) → ₹558 Cr (Y5) with synergies",
        "Free Cash Flow Available for Debt Service (CFADS): ₹144 - 263 Cr/yr",
        "Mandatory Senior Amortization: ₹85 Cr / year (10%)",
        "75% Excess Cash Flow Sweep applied to Senior Debt",
        "Senior Loan Deleveraging: ₹850 Cr entry → <₹20 Cr exit!",
        "Net Debt / EBITDA Ratio: Deleveraged from 3.08x to 0.20x!",
        "5-Year Project LBO IRR Boosted: 14.2% Base → 18.7% (2.36x MoIC)",
    ]
    curr_y = 62
    for p in sweep_pts:
        ax.text(56, curr_y, f"• {p}", fontsize=8.8, color="#E2E8F0")
        curr_y -= 6.0

    plt.tight_layout()
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()


def render_scene5_deliverables(out_path: str):
    """Scene 5: Wall Street Excel Model & Streamlit Deal Room."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#070B14")
    ax.set_facecolor("#070B14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 91, "STAGE 4: WALL STREET DELIVERABLES & INTERACTIVE APP", fontsize=20, fontweight="bold", color="#EC4899", ha="center")
    ax.text(50, 85, "Ready for Investment Banking, M&A Advisory, and Private Equity Evaluation", fontsize=11, color="#94A3B8", ha="center")

    box1 = patches.FancyBboxPatch(
        (8, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#217346",
        linewidth=2,
    )
    ax.add_patch(box1)
    ax.text(28, 71, "[1] 6-Tab Wall Street Excel Workbook", fontsize=13, fontweight="bold", color="#34D399", ha="center")

    ex_pts = [
        "Path: models/Cross_Border_MA_LBO_Model_4200Cr.xlsx",
        "Tab 1: Kaggle_M&A_Target_Screener (Top 25 screened targets)",
        "Tab 2: Sources_Uses_&_Goodwill_PPA (PPA, Goodwill, DTL)",
        "Tab 3: 5Yr_ProForma_IS_&_Synergies (₹380 Cr Phased Synergies)",
        "Tab 4: EPS_Accretion_Dilution_Bridge (+6.4% Accretion)",
        "Tab 5: 5_Debt_Structures_&_Cash_Sweep (Covenant & FCF sweep)",
        "Tab 6: Sensitivity_Matrices (Multiples vs Synergies & LBO IRR)",
    ]
    curr_y = 62
    for p in ex_pts:
        ax.text(12, curr_y, f"• {p}", fontsize=8.8, color="#E2E8F0")
        curr_y -= 6.0

    box2 = patches.FancyBboxPatch(
        (52, 20), 40, 58,
        boxstyle="round,pad=0.8,rounding_size=1.5",
        facecolor="#0F172A",
        edgecolor="#FF4B4B",
        linewidth=2,
    )
    ax.add_patch(box2)
    ax.text(72, 71, "[2] Interactive Streamlit Deal Room", fontsize=13, fontweight="bold", color="#F87171", ha="center")

    st_pts = [
        "Live Web App: streamlit run app.py (http://localhost:8501)",
        "Tab 1: Kaggle Screener & Universal Ticker Deal Matcher",
        "Tab 2: Accretion/Dilution Engine & Plotly Waterfall Chart",
        "Tab 3: Capital Structure & LBO IRR Simulator",
        "Interactive Sliders for Entry Multiple & Synergy Realization",
        "Instant One-Click Wall Street Excel (.xlsx) Download",
        "GitHub: github.com/shreshth-nanda83/ma-accretion-dilution-lbo-model",
    ]
    curr_y = 62
    for p in st_pts:
        ax.text(56, curr_y, f"• {p}", fontsize=8.8, color="#E2E8F0")
        curr_y -= 6.0

    plt.tight_layout()
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()


def generate_introductory_video(output_video_path: str = VIDEO_OUTPUT_PATH):
    """Renders slides, records voiceovers, and compiles into an MP4 video."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)

    scenes_def = [
        {
            "id": 1,
            "render_func": render_scene1_title,
            "script": "Welcome to the Cross-Border M&A Accretion Dilution and LBO Synergy Model. This institutional platform combines real Kaggle NYSE financial data with advanced Wall Street financial engineering to evaluate large-scale cross-border acquisitions."
        },
        {
            "id": 2,
            "render_func": render_scene2_ingestion,
            "script": "Powered by the Kaggle NYSE fundamentals dataset, our engine cleans 79 financial variables across 448 companies into an indexed SQLite database. Using institutional SQL window functions, it screens companies based on EBITDA margins above 15 percent and high cost synergy runways."
        },
        {
            "id": 3,
            "render_func": render_scene3_engine,
            "script": "Calibrated to a flagship 4,200 Crore Rupee deal at 12 times EV to EBITDA, the engine models 380 Crore Rupees in phased synergies, complete Purchase Price Allocation, and proves that Acquirer standalone EPS grows from 45 Rupees to 47.88 Rupees in Year 2, generating a 6.4 percent EPS accretion."
        },
        {
            "id": 4,
            "render_func": render_scene4_lbo,
            "script": "The platform evaluates five debt-to-equity financing structures. Structure 4, an optimal hybrid mix, keeps Net Debt to EBITDA strictly at 3.08 times, beating the 3.2 times covenant ceiling, while boosting 5-year project IRR from 14.2 percent to 18.7 percent via an active 75 percent cash sweep."
        },
        {
            "id": 5,
            "render_func": render_scene5_deliverables,
            "script": "All results are delivered through an automated 6-tab Wall Street Excel workbook and an interactive Streamlit Deal Room featuring dynamic scenario simulation. Ready for investment banking and private equity advisory."
        },
    ]

    scene_video_files = []

    for sc in scenes_def:
        sc_id = sc["id"]
        img_path = os.path.join(SCRATCH_DIR, f"scene_{sc_id}.png")
        wav_path = os.path.join(SCRATCH_DIR, f"scene_{sc_id}.wav")
        mp4_path = os.path.join(SCRATCH_DIR, f"scene_{sc_id}.mp4")

        print(f"[VideoGen] Rendering Scene {sc_id} Slide Image...")
        sc["render_func"](img_path)

        print(f"[VideoGen] Synthesizing Scene {sc_id} Voiceover via TTS Worker...")
        tts_cmd = [sys.executable, TTS_WORKER_SCRIPT, sc["script"], wav_path]
        subprocess.run(tts_cmd, check=True)

        duration = get_wav_duration(wav_path)
        print(f"           Scene {sc_id} Audio Duration: {duration:.2f} seconds")

        print(f"[VideoGen] Encoding Scene {sc_id} MP4...")
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1",
            "-framerate", "24",
            "-i", img_path,
            "-i", wav_path,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", f"{duration + 0.3:.2f}",
            mp4_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[VideoGen] Error in Scene {sc_id}: {res.stderr}")
            raise RuntimeError(f"FFmpeg failed for scene {sc_id}")
        scene_video_files.append(mp4_path)

    # Concatenate all scenes into final video
    concat_txt_path = os.path.join(SCRATCH_DIR, "concat_list.txt")
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for v in scene_video_files:
            norm_v = v.replace("\\", "/")
            f.write(f"file '{norm_v}'\n")

    print(f"[VideoGen] Concatenating {len(scene_video_files)} scenes into master video...")
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt_path,
        "-c", "copy",
        output_video_path
    ]
    res_concat = subprocess.run(concat_cmd, capture_output=True, text=True)
    if res_concat.returncode != 0:
        print(f"[VideoGen] Concat error: {res_concat.stderr}")
        raise RuntimeError("FFmpeg concat failed")

    # Clean up scratch files
    shutil.rmtree(SCRATCH_DIR, ignore_errors=True)

    print(f"[VideoGen] Successfully created introductory video at: {output_video_path}")
    print(f"            Video Size: {os.path.getsize(output_video_path) / (1024*1024):.2f} MB")
    return output_video_path


if __name__ == "__main__":
    generate_introductory_video()
