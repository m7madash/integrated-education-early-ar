# Fajr Science: The Optics of Dawn

## Introduction

The phenomenon of dawn (الفجر) has two distinct optical phases recognized in Islamic jurisprudence and observable in nature:

1. **False Dawn (الفجر الكاذب)** — called *al-fajr al-kadhib* (الفجر الكاذب)
2. **True Dawn (الفجر الصادق)** — called *al-fajr al-sadiq* (الفجر الصادق)

This document explains the physical optics that differentiate them.

---

## Optical Characteristics

### False Dawn (الكاذب)

- **Shape:** Vertical column or streak (ذيل السرحان)
- **Orientation:** Longitudinal along the meridian, perpendicular to horizon
- **Appearance:** First appears as a bright vertical beam rising from the east
- **Duration:** 15–30 minutes, then dissipates
- **Intensity:** Moderate (not spreading widely)
- **Color:** Often white or slightly bluish, less intense

**Why it occurs:** Sunlight scattering in the upper atmosphere (mesospheric dust) creating a vertical illumination column before true twilight.

### True Dawn (الصادق)

- **Shape:** Horizontal band across the entire eastern horizon
- **Orientation:** Latitudinal, parallel to horizon, touching it
- **Appearance:** Spreads from horizon upward, broad glow
- **Duration:** Grows until sunrise
- **Intensity:** Stronger, warm colors (yellow, orange, red)
- **Color:** Golden-red to bright white

**Why it occurs:** Sunlight directly scattering in the lower atmosphere (troposphere) when sun is ~18° below horizon.

---

## Quantitative Thresholds

The transition from false to true dawn corresponds to solar depression angle:

| Latitude Zone | Solar Angle for True Dawn |
|---------------|--------------------------|
| Tropical (0–23.5°) | -12° |
| Subtropical (23.5–35°) | -15° |
| Mid-latitude (35–55°) | -18° |
| High-latitude (55–66.5°) | -21° |
| Arctic (>66.5°) | -24° |

*These angles are approximate and adjusted for refraction.*

---

## Image Processing Features

To distinguish programmatically:

1. **Aspect Ratio of Bright Region**  
   - False dawn: aspect_ratio = height/width > 2.5 (tall and thin)  
   - True dawn: aspect_ratio < 1.5 (short and wide)

2. **Horizontal Spread**  
   - Fraction of columns containing bright pixels  
   - False dawn: < 0.25 (narrow)  
   - True dawn: > 0.40 (broad)

3. **Intensity Distribution**  
   - False dawn: peak intensity localized vertically  
   - True dawn: intensity spreads horizontally

4. **Temporal Behavior**  
   - False dawn appears then vanishes  
   - True dawn monotonically increases

---

## Camera Setup Considerations

- **Field of View:** ~30° of eastern horizon, no obstructions
- **Resolution:** ≥ 1920×1080 to capture fine detail
- **Exposure:** Manual, fixed (to avoid auto-adjustment flicker)
- **Interval:** Every 10–15 seconds during 3–6 AM

---

## References

- Al-Albani, *Sahih al-Jami`* 2031 (Hadith on two dawns)
- Islamic jurisprudence on Fajr times (various madhhabs agree on distinction)
- Atmospheric optics textbooks: *Meteorological Optics* by Mack, *Light and Color in Nature* by Lynch
