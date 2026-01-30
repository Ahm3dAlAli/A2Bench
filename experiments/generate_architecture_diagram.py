#!/usr/bin/env python3
"""
Generate architecture diagram for A²-Bench paper.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import matplotlib.lines as mlines

# Set up the figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# ========== Left Panel: Dual-Control Architecture ==========
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title('(a) Dual-Control Security Model', fontsize=14, fontweight='bold', pad=20)

# Environment/State (center)
env_box = FancyBboxPatch((3, 4), 4, 2, boxstyle="round,pad=0.1",
                         edgecolor='black', facecolor='lightgray', linewidth=2)
ax1.add_patch(env_box)
ax1.text(5, 5, 'Shared State\n$S = S_{world} \\times S_{history} \\times S_{security}$',
         ha='center', va='center', fontsize=11, fontweight='bold')

# Agent (left)
agent_box = FancyBboxPatch((0.5, 4.5), 1.8, 1, boxstyle="round,pad=0.1",
                           edgecolor='darkblue', facecolor='lightblue', linewidth=2)
ax1.add_patch(agent_box)
ax1.text(1.4, 5, 'Agent\n$A_{agent}$', ha='center', va='center',
         fontsize=10, fontweight='bold')

# Adversary (right)
adv_box = FancyBboxPatch((7.7, 4.5), 1.8, 1, boxstyle="round,pad=0.1",
                         edgecolor='darkred', facecolor='#ffcccc', linewidth=2)
ax1.add_patch(adv_box)
ax1.text(8.6, 5, 'Adversary\n$A_{adv}$', ha='center', va='center',
         fontsize=10, fontweight='bold', color='darkred')

# Safety Monitor (top)
monitor_box = FancyBboxPatch((3.5, 7.2), 3, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='darkgreen', facecolor='lightgreen', linewidth=2)
ax1.add_patch(monitor_box)
ax1.text(5, 7.6, 'Safety Monitor: $\\Psi, \\Phi, \\Delta$', ha='center', va='center',
         fontsize=10, fontweight='bold')

# Arrows from agent to state
arrow1 = FancyArrowPatch((2.3, 5), (3, 5), arrowstyle='->', mutation_scale=20,
                        linewidth=2, color='blue')
ax1.add_patch(arrow1)
ax1.text(2.65, 5.3, 'Actions', ha='center', fontsize=9, color='blue')

# Arrows from adversary to state
arrow2 = FancyArrowPatch((7.7, 5), (7, 5), arrowstyle='->', mutation_scale=20,
                        linewidth=2, color='red')
ax1.add_patch(arrow2)
ax1.text(7.35, 5.3, 'Attacks', ha='center', fontsize=9, color='red')

# Observations back to agent
arrow3 = FancyArrowPatch((3, 4.7), (2.3, 4.7), arrowstyle='->', mutation_scale=20,
                        linewidth=1.5, color='blue', linestyle='dashed')
ax1.add_patch(arrow3)
ax1.text(2.65, 4.4, 'Obs', ha='center', fontsize=9, color='blue')

# Observations back to adversary
arrow4 = FancyArrowPatch((7, 4.7), (7.7, 4.7), arrowstyle='->', mutation_scale=20,
                        linewidth=1.5, color='red', linestyle='dashed')
ax1.add_patch(arrow4)
ax1.text(7.35, 4.4, 'Obs', ha='center', fontsize=9, color='red')

# Monitor checking state
arrow5 = FancyArrowPatch((5, 6), (5, 7.2), arrowstyle='<->', mutation_scale=20,
                        linewidth=1.5, color='green')
ax1.add_patch(arrow5)
ax1.text(5.5, 6.6, 'Verify', ha='center', fontsize=9, color='green')

# Safety constraints box (bottom left)
constraints_box = Rectangle((0.3, 1.5), 2.5, 2, edgecolor='black',
                           facecolor='#fff9e6', linewidth=1.5)
ax1.add_patch(constraints_box)
ax1.text(1.55, 3.1, 'Safety Constraints ($\\Psi$):', ha='center',
         fontsize=9, fontweight='bold')
ax1.text(1.55, 2.7, '• Invariants', ha='center', fontsize=8)
ax1.text(1.55, 2.4, '• Temporal Props', ha='center', fontsize=8)
ax1.text(1.55, 2.1, '• Security Policies', ha='center', fontsize=8)
ax1.text(1.55, 1.8, '• Compliance Rules', ha='center', fontsize=8)

# Attack strategies box (bottom right)
attacks_box = Rectangle((7.2, 1.5), 2.5, 2, edgecolor='black',
                        facecolor='#ffe6e6', linewidth=1.5)
ax1.add_patch(attacks_box)
ax1.text(8.45, 3.1, 'Attack Strategies:', ha='center',
         fontsize=9, fontweight='bold', color='darkred')
ax1.text(8.45, 2.7, '• Social Engineering', ha='center', fontsize=8)
ax1.text(8.45, 2.4, '• Prompt Injection', ha='center', fontsize=8)
ax1.text(8.45, 2.1, '• State Corruption', ha='center', fontsize=8)
ax1.text(8.45, 1.8, '• Multi-Vector', ha='center', fontsize=8)

# Scoring output (bottom center)
score_box = FancyBboxPatch((3.5, 0.5), 3, 0.8, boxstyle="round,pad=0.05",
                          edgecolor='purple', facecolor='#f0e6ff', linewidth=2)
ax1.add_patch(score_box)
ax1.text(5, 0.9, 'A²-Score = $\\alpha S_{safe} + \\beta S_{sec} + \\gamma S_{rel} + \\delta S_{comp}$',
         ha='center', va='center', fontsize=9, fontweight='bold', color='purple')

# ========== Right Panel: System Architecture ==========
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')
ax2.set_title('(b) A²-Bench System Architecture', fontsize=14, fontweight='bold', pad=20)

# Layer 1: Domain Layer (top)
domain_box = FancyBboxPatch((1, 8.5), 8, 1, boxstyle="round,pad=0.05",
                           edgecolor='navy', facecolor='#e6f2ff', linewidth=2)
ax2.add_patch(domain_box)
ax2.text(5, 9, 'Domain Layer', ha='center', va='center', fontsize=11, fontweight='bold')

# Domain boxes
healthcare = Rectangle((1.5, 8.65), 1.5, 0.5, edgecolor='navy', facecolor='white', linewidth=1)
ax2.add_patch(healthcare)
ax2.text(2.25, 8.9, 'Healthcare', ha='center', fontsize=8, fontweight='bold')

finance = Rectangle((3.5, 8.65), 1.5, 0.5, edgecolor='gray', facecolor='white',
                   linewidth=1, linestyle='dashed')
ax2.add_patch(finance)
ax2.text(4.25, 8.9, 'Finance', ha='center', fontsize=8, color='gray')

industrial = Rectangle((5.5, 8.65), 1.5, 0.5, edgecolor='gray', facecolor='white',
                       linewidth=1, linestyle='dashed')
ax2.add_patch(industrial)
ax2.text(6.25, 8.9, 'Industrial', ha='center', fontsize=8, color='gray')

# Layer 2: Evaluation Engine (middle-top)
eval_box = FancyBboxPatch((1, 6.8), 8, 1.3, boxstyle="round,pad=0.05",
                         edgecolor='darkgreen', facecolor='#e6ffe6', linewidth=2)
ax2.add_patch(eval_box)
ax2.text(5, 7.8, 'Evaluation Engine', ha='center', va='center',
         fontsize=11, fontweight='bold')

# Evaluation components
baseline = Rectangle((1.5, 7), 1.8, 0.5, edgecolor='green', facecolor='white', linewidth=1)
ax2.add_patch(baseline)
ax2.text(2.4, 7.25, 'Baseline Eval', ha='center', fontsize=8)

adversarial = Rectangle((4, 7), 1.8, 0.5, edgecolor='green', facecolor='white', linewidth=1)
ax2.add_patch(adversarial)
ax2.text(4.9, 7.25, 'Adversarial Eval', ha='center', fontsize=8)

metrics = Rectangle((6.5, 7), 1.8, 0.5, edgecolor='green', facecolor='white', linewidth=1)
ax2.add_patch(metrics)
ax2.text(7.4, 7.25, 'Metrics', ha='center', fontsize=8)

# Layer 3: Safety Specification (middle)
spec_box = FancyBboxPatch((1, 5.1), 8, 1.3, boxstyle="round,pad=0.05",
                         edgecolor='purple', facecolor='#f9e6ff', linewidth=2)
ax2.add_patch(spec_box)
ax2.text(5, 6.1, 'Safety Specification Layer', ha='center', va='center',
         fontsize=11, fontweight='bold')

# Spec components
psi = Rectangle((1.5, 5.3), 1.5, 0.5, edgecolor='purple', facecolor='white', linewidth=1)
ax2.add_patch(psi)
ax2.text(2.25, 5.55, '$\\Psi$ (Safety)', ha='center', fontsize=8)

phi = Rectangle((3.5, 5.3), 1.5, 0.5, edgecolor='purple', facecolor='white', linewidth=1)
ax2.add_patch(phi)
ax2.text(4.25, 5.55, '$\\Phi$ (Security)', ha='center', fontsize=8)

delta = Rectangle((5.5, 5.3), 1.5, 0.5, edgecolor='purple', facecolor='white', linewidth=1)
ax2.add_patch(delta)
ax2.text(6.25, 5.55, '$\\Delta$ (Reliability)', ha='center', fontsize=8)

comp = Rectangle((7.2, 5.3), 1.3, 0.5, edgecolor='purple', facecolor='white', linewidth=1)
ax2.add_patch(comp)
ax2.text(7.85, 5.55, 'Compliance', ha='center', fontsize=8)

# Layer 4: Agent Interface (middle-bottom)
agent_interface_box = FancyBboxPatch((1, 3.4), 8, 1.3, boxstyle="round,pad=0.05",
                                     edgecolor='blue', facecolor='#e6f0ff', linewidth=2)
ax2.add_patch(agent_interface_box)
ax2.text(5, 4.4, 'Agent Interface Layer', ha='center', va='center',
         fontsize=11, fontweight='bold')

# Agent types
llm_agent = Rectangle((1.5, 3.6), 1.5, 0.5, edgecolor='blue', facecolor='white', linewidth=1)
ax2.add_patch(llm_agent)
ax2.text(2.25, 3.85, 'LLM Agent', ha='center', fontsize=8)

rl_agent = Rectangle((3.5, 3.6), 1.5, 0.5, edgecolor='blue', facecolor='white', linewidth=1)
ax2.add_patch(rl_agent)
ax2.text(4.25, 3.85, 'RL Agent', ha='center', fontsize=8)

rule_agent = Rectangle((5.5, 3.6), 1.5, 0.5, edgecolor='blue', facecolor='white', linewidth=1)
ax2.add_patch(rule_agent)
ax2.text(6.25, 3.85, 'Rule-Based', ha='center', fontsize=8)

# Layer 5: Models (bottom)
models_box = FancyBboxPatch((1, 1.7), 8, 1.3, boxstyle="round,pad=0.05",
                           edgecolor='orange', facecolor='#fff5e6', linewidth=2)
ax2.add_patch(models_box)
ax2.text(5, 2.7, 'Model Layer', ha='center', va='center',
         fontsize=11, fontweight='bold')

# Model instances
gpt4 = Rectangle((1.8, 1.9), 1.3, 0.5, edgecolor='orange', facecolor='white', linewidth=1)
ax2.add_patch(gpt4)
ax2.text(2.45, 2.15, 'GPT-4', ha='center', fontsize=8, fontweight='bold')

claude = Rectangle((3.5, 1.9), 1.3, 0.5, edgecolor='orange', facecolor='white', linewidth=1)
ax2.add_patch(claude)
ax2.text(4.15, 2.15, 'Claude-3.7', ha='center', fontsize=8, fontweight='bold')

o4mini = Rectangle((5.2, 1.9), 1.3, 0.5, edgecolor='orange', facecolor='white', linewidth=1)
ax2.add_patch(o4mini)
ax2.text(5.85, 2.15, 'O4-Mini', ha='center', fontsize=8, fontweight='bold')

others = Rectangle((6.9, 1.9), 1.3, 0.5, edgecolor='gray', facecolor='white',
                   linewidth=1, linestyle='dashed')
ax2.add_patch(others)
ax2.text(7.55, 2.15, 'Custom', ha='center', fontsize=8, color='gray')

# Results/Output (very bottom)
results_box = FancyBboxPatch((2, 0.3), 6, 0.8, boxstyle="round,pad=0.05",
                            edgecolor='red', facecolor='#ffe6e6', linewidth=2)
ax2.add_patch(results_box)
ax2.text(5, 0.7, 'Output: Safety/Security/Reliability/Compliance Scores + Violation Reports',
         ha='center', va='center', fontsize=9, fontweight='bold', color='darkred')

# Add connecting arrows between layers
for y_start, y_end in [(8.5, 8.1), (6.8, 6.4), (5.1, 4.7), (3.4, 3.0), (1.7, 1.1)]:
    arrow = FancyArrowPatch((5, y_start), (5, y_end), arrowstyle='->',
                           mutation_scale=20, linewidth=2, color='black', alpha=0.6)
    ax2.add_patch(arrow)

plt.tight_layout()
plt.savefig('paper/figures/architecture.pdf', format='pdf', bbox_inches='tight', dpi=300)
print("Architecture diagram saved to: paper/figures/architecture.pdf")
