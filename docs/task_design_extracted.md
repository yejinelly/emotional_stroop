# Emotional Word Stroop Task - Design Elements Extracted

**Source**: mario-bermonti/emo_stroop_task (Spanish version)

## Task Overview

- **Type**: Color-word Stroop task with emotional valence words
- **Language**: Spanish (needs Korean translation)
- **Total trials**: 144 experimental + 24 practice
- **Conditions**: Positive, Negative, Neutral words
- **Colors**: Blue, Green, Red

---

## Color-Response Mapping

| Color | Key Response | Notes |
|-------|-------------|-------|
| **Red** | `f` | Left hand index finger |
| **Green** | `j` | Right hand index finger |
| **Blue** | `space` | Thumb |

**Korean version will need**: Korean color names and potentially different key mapping if needed.

---

## Practice Trials

**Total**: 24 trials
- **Word stimuli**: Color words only (azul=blue, rojo=red, verde=green)
- **Condition**: All congruent (word matches color)
- **Structure**: 4 blocks × 6 trials
- **Randomization**: Blocks are shuffled

**Timing (Practice)**:
1. Instructions
2. Fixation cross: **1.0 sec**
3. Blank screen: **0.5 sec**
4. Word stimulus: **Until response** (no time limit)
5. Feedback: Displayed after response

**Practice trial file**: `practice_trials.csv` (6 trials, repeated)

---

## Experimental Trials

**Total**: 144 trials
- **Positive words**: 48
- **Negative words**: 48
- **Neutral words**: 48
- **Each word presented**: Once only

**Block structure**:
- **Total blocks**: 16 blocks
- **Trials per block**: 9 trials
  - 3 positive (1 per color)
  - 3 negative (1 per color)
  - 3 neutral (1 per color)
- **Large experimental blocks**: 4 × 36 trials
- **Rest breaks**: 3 breaks (after each 36-trial block)

**Timing (Experimental)**:
1. Instructions
2. Fixation cross: **0.5 sec**
3. Blank screen: **0.5 sec**
4. Word stimulus: **Until response** (no time limit)
5. **No feedback**

---

## Word Lists (Spanish)

### Example Positive Words
- luna, paseo, cantar, jugar, fortuna, sonrisa, bienestar, sincero, amar, baile, etc.
- Total: 48 words

### Example Negative Words
- pedo, herir, escupir, lesionar, falsear, terremoto, repugnar, muro, celda, padecer, etc.
- Total: 48 words

### Example Neutral Words
- giro, forma, llamar, ancho, atender, similar, inscribir, producto, orar, frase, etc.
- Total: 48 words

**Full word list**: See `exp_trials.csv` (lines 2-145)

**Word characteristics**:
- Balanced for word length across conditions
- Spanish vocabulary (needs Korean translation/adaptation)

---

## Trial Balance

Each block (9 trials) has perfect balance:

| Condition | Blue | Green | Red | Total per block |
|-----------|------|-------|-----|-----------------|
| Positive  | 1    | 1     | 1   | 3               |
| Negative  | 1    | 1     | 1   | 3               |
| Neutral   | 1    | 1     | 1   | 3               |
| **Total** | 3    | 3     | 3   | **9**           |

Across all 16 blocks: 48 positive + 48 negative + 48 neutral = **144 trials**

---

## Randomization Strategy

1. **Word list**: Pre-organized into 16 blocks in `exp_trials.csv`
2. **Block ranges**: Specified in `choose_blocks.csv` (0:9, 9:18, 18:27, etc.)
3. **Block shuffling**: Block order is randomized at experiment start
4. **Within-block**: Trials presented in order from CSV (could add within-block shuffle)

---

## Data Recording

**Measured variables**:
- `participant`: Participant ID
- `session`: Session number
- `text`: Word presented
- `letterColor`: Color of the word (blue/green/red)
- `corrAns`: Correct response key (f/j/space)
- `condition`: Valence (positive/negative/neutral)
- `resp_exp.keys`: Participant's response
- `resp_exp.corr`: Accuracy (1=correct, 0=incorrect)
- `resp_exp.rt`: Reaction time (from stimulus onset)

---

## Korean Adaptation Requirements

### 1. Word Translation
- Translate 48 positive, 48 negative, 48 neutral words
- Match word length across conditions
- Validate emotional valence ratings for Korean context

### 2. Color Words (for practice)
- 빨강 (red)
- 초록 (green)
- 파랑 (blue)

### 3. Instructions Translation
- Practice instructions
- Experimental instructions
- Feedback messages

### 4. Key Mapping (optional)
- Keep f/j/space or adapt to Korean keyboard preferences
- Consider: ㄱ/ㄴ/space or other comfortable mapping

---

## Implementation Notes for Streamlit

### Key differences from PsychoPy:
1. **Timing precision**: Streamlit uses JavaScript `setTimeout()` (less precise than PsychoPy)
2. **Keyboard events**: Use `streamlit_javascript` for real-time key detection
3. **Trial flow**: Use `st.session_state` to track trial progression
4. **Randomization**: Pre-shuffle on first load, store in session state

### Required Streamlit components:
- `streamlit_javascript`: For keyboard input and timing
- `pandas`: For CSV reading and trial management
- Custom CSS: For word color display

### File structure:
```
emotional_word_stroop/
├── app.py                    # Main Streamlit app
├── utils/
│   ├── trial_manager.py      # Trial sequence and randomization
│   └── keyboard_handler.py   # Real-time keyboard detection
├── stimuli/
│   ├── korean_words.csv      # Korean word list (to create)
│   └── practice_words.csv    # Korean practice words (to create)
└── data/
    └── responses/            # Participant data storage
```

---

## Next Steps

1. ✅ **Extract task design** (COMPLETED)
2. **Translate word lists to Korean**
   - Find Korean emotional word norms (e.g., Korean Affective Norms, Park et al.)
   - Select 48 positive, 48 negative, 48 neutral words
   - Balance for word length and frequency
3. **Create Korean CSV files**
   - `korean_exp_trials.csv`
   - `korean_practice_trials.csv`
4. **Implement Streamlit version**
   - Set up virtual environment
   - Install dependencies (streamlit, pandas, streamlit-javascript)
   - Build app.py with keyboard detection
   - Test timing precision
5. **Pilot testing**
   - Validate timing accuracy
   - Test with Korean participants for word valence validation
