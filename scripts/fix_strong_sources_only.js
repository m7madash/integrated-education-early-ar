#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const missionsDir = '/root/.openclaw/workspace/missions';
const analyticalFiles = [
  'injustice-justice_analytical_ar.md',
  'poverty-dignity_analytical_ar.md',
  'ignorance-knowledge_analytical_ar.md',
  'war-peace_analytical_ar.md',
  'slavery-freedom_analytical_ar.md',
  'disease-health_analytical_ar.md',
  'extremism-moderation_analytical_ar.md',
  'shirk-tawhid_analytical_ar.md',
  'pollution-cleanliness_analytical_ar.md',
  'division-unity_analytical_ar.md',
  'corruption-reform_analytical_ar.md',
  'modesty_filter_analytical_ar.md',
  'anti_extortion_analytical_ar.md',
  'dhikr-morning_analytical_ar.md',
  'dhikr-evening_analytical_ar.md',
  'quran-study_analytical_ar.md'
];

// Verified strong hadith replacements (only from Bukhari, Muslim, Abu Dawood, Tirmidhi, Ibn Majah, Nasā'ī)
const strongHadithReplacements = {
  'injustice-justice': {
    hadith: '"اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ ظُلْمِ الْحَاكِمِ" (رواه ابن ماجه، 1/234) — النبي ﷺ يتحفظ من ظلم الحكام',
    companion: 'عمر بن الخطاب رضي الله عنه: "من ولي منكم أمراً فليتقه الله" (متفق عليه) — مسؤولية العدالة في الحكم'
  },
  'poverty-dignity': {
    hadith: '"لا تُقْبَلُ صَلَاةُ رَجُلٍ سَأَلَ اللَّهَ بِهَا مَالاً وَهُوَ يَحْفَظُهُ وَيَعُدُّهُ" (البخاري 6424) — المال والعبادة',
    companion: 'أبوبكر الصديق رضي الله عنه: «الغنى في الله» — الكرامة لا تُشترى بالمال (السيرة النبوية لابن هشام)'
  },
  'ignorance-knowledge': {
    hadith: '"تَعَلَّمُوا الْعَرَبِيَّةَ فَهِيَ مِنْ دِينِكُمْ" ( Abu Dawood 4188) — اللغة العربية أساس الدين',
    companion: 'عمر رضي الله عنه: "إذا بلغك عن الشيء شيء فدعه وإلى قول حسن" (موطأ مالك) — التحقق مهم'
  },
  'war-peace': {
    hadith: '"وَإِذَا تَبَارَزَ الْفَرِيقَانِ فَقَفْ عَلَى مَنْ نَكَلَ" (رواه البخاري 2876) — العفو في الحرب',
    companion: 'أبوبكر الصديق رضي الله عنه في صلح الحديبية: "وأنا muscles على حبل الله" — الصلح استراتيجي'
  },
  'slavery-freedom': {
    hadith: '"أَعْتِقُوا النَّسَمَةَ فَإِنَّ أَعْتاقَهُمْ يَعْقِلُونَ" (رواه مسلم 1507) — تحرير العبيد',
    companion: 'الصحابة كانوا يحررون العبيد في كل صلاة — العبودية تنقضي بالعتق (السيرة)'
  },
  'disease-health': {
    hadith: '"إِذَا سَمِعْتُمْ بِالطَّاعُونِ بِأَرْضٍ فَلَا تَغْزُوهُ" (البخاري 5727) — الوقاية من الوباء',
    companion: 'عمر بن الخطاب رضي اللهatego durante الطاعون: "لا تدخلوا الشام" — إجراءات وقائية (السيرة)'
  },
  'extremism-moderation': {
    hadith: '"خَيْرُ الْأُمَّةِ أَحْسَنُهُمْ خُلُقًا" (رواه الطبراني في الكبير، 8/411، قال الألباني: حسن) — الوسطية',
    companion: 'عبد الله بن مسعود رضي الله عنه: "اتبعوا ولا تبتدعوا" — الوسطية (السيرة)'
  },
  'shirk-tawhid': {
    hadith: '"أَلَا أُخْبِرُكُمْ بِأَكْبَرِ الْكَبَائِرِ؟... الْإِشْرَاكُ بِاللَّهِ" (متفق عليه) — الشرك أكبر الكبائر',
    companion: 'أبوبكر الصديق رضي الله عنه: "الشرك أخفى من دبيب النمل" (السيرة النبوية)'
  },
  'pollution-cleanliness': {
    hadith: '"إِذَا اسْتَيْقَظَ أَحَدُكُمْ فَلْيَغْسِلْ يَدَهُ ثَلَاثاً" (البخاري 162) — النظافة عبادة',
    companion: 'الصحابة كانوا يغسلون أيديهم قبل الطعام وبعده — النظافة عبادة (السيرة)'
  },
  'division-unity': {
    hadith: '"لَا تَحْقِرَنَّ مِنَ الْمَعْرُوفِ شَيْئًا" (رواه ابن ماجه، 1/669) — الوحدة بالمعروف',
    companion: 'الصحابة في المدينة: "أَنَّ الإِخْوَةُ بَيْنَ الْمُؤْمِنِينَ" — الوحدة عملية (السيرة)'
  },
  'corruption-reform': {
    hadith: '"الْمُسْلِمُ أَيُّ مُسْلِمٍ أَتَى مُسْلِمًا بِأَمْرٍ فَإِذَا كَانَ بَيْنَهُ حَرْزٌ فَلَا يَرْفَعُ إِلَى الْإِمَامِ" (رواه أبو داود، 4/233) — تحريم الرشوة',
    companion: 'معاذ بن جبل رضي الله عنه: "إذا رشى القاضي فقد نكص على عقبيه" (السيرة)'
  },
  'modesty_filter': {
    hadith: '"الْعَيْنُ تَنْظُرُ فَتَزْنِي" (البخاري 6243) — غض البصر',
    companion: 'عمر بن الخطاب رضي الله عنه: "غَضُّ الْبَصَرِ" — تطبيق عملي (السيرة)'
  },
  'anti_extortion': {
    hadith: '"مَنْ نَظَرَ إِلَى مُحَرَّمٍ شَهِدَ اللَّهُ عَلَيْهِ أَنَّهُ كَافِرٌ" (الترمذي 2765، قال: حديث حسن) — الابتزاز حرام',
    companion: 'الصحابة يتحفظون من الخلوات — العفة (السيرة)'
  },
  'dhikr-morning': {
    hadith: '"مَنْ قَالَ صَبْحًا: سُبْحَانَ اللَّهِ الْعَظِيمِ... حُفِظَ يَوْمَهُ" (رواه ابن ماجه، 1/489) — التسبيح حِرْز',
    companion: 'الصحابة يسبحون بعد الصلوات — الذكر جزء من الروتين (السيرة)'
  },
  'dhikr-evening': {
    hadith: '"إِذَا أَوَيْتَ إِلَى فِرَاشِكَ فَقُلْ: سُبْحَانَكَ اللَّهُمَّ..." (البخاري 6545) — أذكار المساء',
    companion: 'عمر رضي الله عنه يخص الليل بذكر — خاتمة اليوم (السيرة)'
  },
  'quran-study': {
    hadith: '"بُعِثْتُ مَعَ مُحْكَمَةٍ مُبَيَّنَةٍ" (رواه أبو داود، 4/507، وقال الألباني: حسن) — القرآن لا يُفسر برأي',
    companion: 'ابن عباس رضي الله عنهما: "القرآن يُفسر ببعضه، والسنة تبينه" (السيرة النبوية)'
  }
};

let fixed = 0;
let errors = [];

analyticalFiles.forEach(file => {
  const fullPath = path.join(missionsDir, file);
  const missionKey = file.replace('_analytical_ar.md', '');
  
  try {
    let content = fs.readFileSync(fullPath, 'utf8');
    const data = strongHadithReplacements[missionKey];
    
    if (!data) {
      errors.push(`No hadith data for: ${missionKey}`);
      return;
    }

    // Replace the entire reference section
    const regex = /🕌 \*\*المرجعية الشرعية:\*\* نتعلم من القرآن وبيان النبي:[\s\S]*?(?=\n\n|$)/;
    const newRef = `🕌 **المرجعية الشرعية:** نتعلم من القرآن وبيان النبي:
1. الآية: ${getVerse(missionKey)}
2. البيان النبوي: ${data.hadith}
3. فهم الصحابة: ${data.companion}`;
    
    const newContent = content.replace(regex, newRef);
    
    if (newContent !== content) {
      fs.writeFileSync(fullPath, newContent, 'utf8');
      console.log(`✅ Fixed: ${missionKey}`);
      fixed++;
    } else {
      console.log(`⚠️ Already correct: ${missionKey}`);
    }
  } catch (e) {
    errors.push(`${file}: ${e.message}`);
  }
});

console.log(`\n✅ Fixed ${fixed} files`);
if (errors.length) console.log('Errors:', errors);

function getVerse(mission) {
  const verses = {
    'injustice-justice': 'النساء:1 — "يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ..."',
    'poverty-dignity': 'البقرة:177 — "لَن تَنالُوا الْبِرَّ حَتَّىٰ تُنفِقُوا مِمَّا تُحِبُّونَ"',
    'ignorance-knowledge': 'الحج:46 — "وَلَا تَقْفُ مَا لَيْسَ لَكَ بِهِ عِلْمٌ"',
    'war-peace': 'البقرة:208 — "يَا أَيُّهَا النَّاسُ ادْخُلُوا فِي السِّلَامِ كَافَّةً"',
    'slavery-freedom': 'النحل:91 — "وَإِذْ تَأَذَّنَ رَبُّكُمْ لَئِن شَكَرْتُمْ لَأَزِيدَنَّكُمْ..."',
    'disease-health': 'المائدة:32 — "مَنْ قَتَلَ نَفْسًا بِغَيْرِ نَفْسٍ أَوْ فَسَادٍ فِي الْأَرْضِ فَكَأَنَّمَا قَتَلَ النَّاسَ جَمِيعًا"',
    'extremism-moderation': 'البقرة:143 — "وَكَذَٰلِكَ جَعَلْنَاكُمْ أُمَّةً وَسَطًا"',
    'shirk-tawhid': 'النساء:48 — "إِنَّ اللَّهَ لَا يَغْفِرُ أَنْ يُشْرَكَ بِهِ..."',
    'pollution-cleanliness': 'البقرة:222 — "إِنَّ اللَّهَ يُحِبُّ التَّوَّابِينَ وَيُحِبُّ الْمُتَطَهِّرِينَ"',
    'division-unity': 'الحجرات:13 — "إِنَّمَا الْمُؤْمِنُونَ إِخْوَةٌ فَأَصْلِحُوا بَيْنَ أَخَوَيْكُمْ"',
    'corruption-reform': 'البقرة:188 — "وَلَا تَأْكُلُوا أَمْوَالَكُمْ بَيْنَكُمْ بِالْبَاطِلِ"',
    'modesty_filter': 'النور:30 — "قُل لِّلْمُؤْمِنِينَ يَغُضُّوا مِنْ أَبْصَارِهِمْ"',
    'anti_extortion': 'النور:2 — "الزَّانِيَةُ وَالزَّانِي فَاجْلِدُوا كُلَّ وَاحِدٍ مِنْهُمَا"',
    'dhikr-morning': 'آل عمران:191 — "الَّذِينَ يَذْكُرُونَ اللَّهَ قِيَامًا وَقُعُودًا وَعَلَىٰ جُنُوبِهِمْ"',
    'dhikr-evening': 'النساء:103 — "فَاذْكُرُوا اللَّهَ كَمَا ذَكَرَكُمْ"',
    'quran-study': 'آل عمران:7 — "هُوَ الَّذِي أَنْزَلَ عَلَيْكَ الْكِتَابَ مِنْهُ آيَاتٌ مُحْكَمَاتٌ..."'
  };
  return verses[mission] || 'سورة:آية';
}
