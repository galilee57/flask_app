---
title: 💪 Strength Training Project – Force, Hypertrophy & Endurance Calculation
summary: English Version
---

**This project analyzes strength training sessions based on simple data**: number of repetitions, load used, and total training volume.

For each exercise, the application calculates the training volume (load × repetitions × sets), and then interprets the session according to repetition ranges commonly associated with specific training goals:

→ Low repetitions with heavy loads → strength-oriented training  
→ Moderate repetitions with significant volume → hypertrophy-oriented training  
→ High repetitions with lighter loads → muscular endurance-oriented training

These metrics are then aggregated across the entire session to estimate the actual distribution of work between strength, hypertrophy, and endurance.

This allows the user to:

→ understand what is truly being trained beyond subjective perception  
→ compare different sessions over time  
→ adjust volume or repetitions to better target specific goals

The calculation is based on a weighted distribution centered around the number of repetitions performed.  
For each repetition count, a portion of the total volume is allocated to strength, hypertrophy, and endurance according to normalized coefficients (whose sum equals 1).

This approach smooths the analysis and better reflects the physiological reality of resistance training, where adaptation zones overlap rather than exist as rigid boundaries.

The load ↔ repetitions ↔ adaptations model implemented in this application is based on the well-documented concept of the _repetition continuum_, which suggests that different repetition ranges and loads promote different adaptations (strength, hypertrophy, endurance) in resistance training. Scientific reviews also confirm that total training volume plays a central role in muscle development, which justifies the use of a weighted distribution model rather than fixed repetition thresholds.

---

📚 **Scientific References**

The calculation principles used in this project are based on established research in exercise science, particularly regarding the relationship between load, repetition count, total volume, and physiological adaptations (strength, hypertrophy, endurance).

Schoenfeld, B. J. (2010).  
_The mechanisms of muscle hypertrophy and their application to resistance training._  
Journal of Strength and Conditioning Research, 24(10), 2857–2872.  
→ Foundational article explaining the mechanisms of muscle hypertrophy and the role of training volume.

Schoenfeld, B. J., Grgic, J., Ogborn, D., & Krieger, J. W. (2017).  
_Strength and hypertrophy adaptations between low- vs. high-load resistance training._  
Journal of Strength and Conditioning Research, 31(12), 3508–3523.  
→ Shows that different repetition ranges can produce similar hypertrophy when volume is equated.

Schoenfeld, B. J., & Grgic, J. (2018).  
_Evidence-based guidelines for resistance training volume to maximize muscle hypertrophy._  
Strength and Conditioning Journal, 40(4), 107–112.  
→ Highlights the importance of total volume rather than strict repetition thresholds.

Campos, G. E. R., et al. (2002).  
_Muscular adaptations in response to three different resistance-training regimens._  
European Journal of Applied Physiology, 88, 50–60.  
→ Foundational study illustrating the strength–hypertrophy–endurance continuum across repetition ranges and loads.

American College of Sports Medicine (ACSM). (2009).  
_Progression models in resistance training for healthy adults._  
Medicine & Science in Sports & Exercise, 41(3), 687–708.  
→ Official recommendations on repetition ranges and their relationship to muscular adaptations.
