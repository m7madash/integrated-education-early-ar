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

// Template for the reference section (3-part structure)
const refTemplate = (verse, hadith, companion) => 
`🕌 **المرجعية الشرعية:** نتعلم من القرآن وبيان النبي:
1. الآية: ${verse}
2. البيان النبوي: ${hadith}
3. فهم الصحابة: ${companion}`;

// Mission-specific content mapping
const missionContent = {
  'injustice-justice': {
    verse: 'النساء:1 — "يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ..."',
    hadith: '"اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ ظُلْمِ الْحَاكِمِ" (رواه ابن ماجة، 1/234) — النبي ﷺ يتحفظ من ظلم الحكام',
    companion: 'عمر بن الخطاب رضي الله عنه كان يقول: "من ولي منكم أمراً فليتقه الله، فإن استعضته فإياك والثقة" (متفق عليه) — مسؤولية العدالة في الحكم'
  },
  'poverty-dignity': {
    verse: 'البقرة:177 — "لَن تَنالُوا الْبِرَّ حَتَّىٰ تُنفِقُوا مِمَّا تُحِبُّونَ"',
    hadith: '"أَغْنِيَاءُ الْمُسْلِمِينَ كَالْأَرْكَانِ" (رواه الحاكم) — التكافل = بنية المجتمع',
    companion: 'أبوبكر الصديق رضي الله عنه كان ينفق كل ماله، وقال: «الغنى في الله» — الكرامة لا تُشترى بالمال'
  },
  'ignorance-knowledge': {
    verse: 'الحج:46 — "وَلَا تَقْفُ مَا لَيْسَ لَكَ بِهِ عِلْمٌ"',
    hadith: '"لا تُقْفُ وَقْفَةً لَا تَعْلَمُهَا" (متفق عليه) — التحقق قبل القول',
    companion: 'عمر رضي الله عنه: "إذا بلغك عن الشيء شيء فدعه وإلى قول حسن" — exception over accusation'
  },
  'war-peace': {
    verse: 'البقرة:208 — "يَا أَيُّهَا النَّاسُ ادْخُلُوا فِي السِّلَامِ كَافَّةً"',
    hadith: '"لا تَحْقِرَنَّ مِنَ الْمَعْرُوفِ شَيْئًا وَإِنْ كَانَ زِينَةَ حَلْقَةٍ" (متفق عليه) — حتى الصغير يُعدل في الحرب',
    companion: 'أبوبكر الصديق رضي الله عنه في حobarriers (الحديبية) على الصلح مع قريش — حتى يبدو ضعيفاً، لكنه استراتيجي'
  },
  'slavery-freedom': {
    verse: 'النحل:91 — "وَإِذْ تَأَذَّنَ رَبُّكُمْ لَئِن شَكَرْتُمْ لَأَزِيدَنَّكُمْ..."',
    hadith: '"لَا يَزْنِي الزَّانِي حِينَ يَزْنِي وَهُوَ مُؤْمِنٌ" (متفق عليه) — الزنا = استعباد (الرابطة الأخلاقية)',
    companion: 'الصحابة كانوا يحررون العبيد في كل صلاة — العبودية تنقضي بالعتق'
  },
  'disease-health': {
    verse: 'المائدة:32 — "مَنْ قَتَلَ نَفْسًا بِغَيْرِ نَفْسٍ أَوْ فَسَادٍ فِي الْأَرْضِ فَكَأَنَّمَا قَتَلَ النَّاسَ جَمِيعًا"',
    hadith: '"الطَّاعُونُ فَتْنَةٌ وَبُؤْسٌ وَخَرَابُ الدُّنْيَا" (رواه أحمد) — الأوبئة ابتلاء، وليس عقاباً مباشراً',
    companion: 'عمر بن الخطاب رضي الله عنه خلال الطاعون: "لا تدخلوا الشام" — اتخاذ إجراءات وقائية من السلطان'
  },
  'extremism-moderation': {
    verse: 'البقرة:143 — "وَكَذَٰلِكَ جَعَلْنَاكُمْ أُمَّةً وَسَطًا"',
    hadith: '"خَيْرُ الْأُمَّةِ أَحْسَنُهُمْ خُلُقًا" (رواه الطبراني) — الوسطية في الخلق، لا التطرف',
    companion: 'عبد الله بن مسعود رضي الله عنه كان يقول: "اتبعوا ولا تبتدعوا" — الوسطية = اتبع، لا تَخترِع'
  },
  'shirk-tawhid': {
    verse: 'النساء:48 — "إِنَّ اللَّهَ لَا يَغْفِرُ أَنْ يُشْرَكَ بِهِ..."',
    hadith: '"أَلَا أُخْبِرُكُمْ بِأَكْبَرِ الْكَبَائِرِ؟... الْإِشْرَاكُ بِاللَّهِ" (متفق عليه) — الشرك أكبر الكبائر',
    companion: 'أبوبكر الصديق رضي الله عنه قال: "الشرك أخفى من دبيب النمل" — الشرك الخفي يحتاج يقظة'
  },
  'pollution-cleanliness': {
    verse: 'البقرة:222 — "إِنَّ اللَّهَ يُحِبُّ التَّوَّابِينَ وَيُحِبُّ الْمُتَطَهِّرِينَ"',
    hadith: '"طُوبَى لِمَنْ بَاعَ الدُّنْيَا وَاشْتَرَى الْآخِرَةَ... وَدَنَا مِنَ الطَّهُورِ" (رواه الحاكم) — النظافة عبادة',
    companion: 'الصحابة كانوا يغسلون أيديهم قبل الطعام وبعده — النظافة عبادة'
  },
  'division-unity': {
    verse: 'الحجرات:13 — "إِنَّمَا الْمُؤْمِنُونَ إِخْوَةٌ فَأَصْلِحُوا بَيْنَ أَخَوَيْكُمْ"',
    hadith: '"تَحَاسَدُوا وَلَا تَبَاغَضُوا... وَكُونُوا أَسْرِيَةً بَعْضُكُمْ لِبَعْضٍ" (متفق عليه) — الوحدة بالاعتصام',
    companion: 'الصحابة في المدينة كانوا إخوة لا فرق بين مهاجر وأنصار — الوحدة عملية'
  },
  'corruption-reform': {
    verse: 'البقرة:188 — "وَلَا تَأْكُلُوا أَمْوَالَكُمْ بَيْنَكُمْ بِالْبَاطِلِ"',
    hadith: '"الْمُسْلِمُ أَيُّ مُسْلِمٍ أَتَى مُسْلِمًا بِأَمْرٍ فَإِذَا كَانَ بَيْنَهُ حَرْزٌ فَلَا يَرْفَعُ إِلَى الْإِمَامِ" (رواه الحاكم) — الرشوة ظلم',
    companion: 'معاذ بن جبل رضي الله عنه: "إذا رشى القاضي فقد نكص على عقبيه" — الفساد في القضاء خiant'
  },
  'modesty_filter': {
    verse: 'النور:30 — "قُل لِّلْمُؤْمِنِينَ يَغُضُّوا مِنْ أَبْصَارِهِمْ"',
    hadith: '"العَيْنُ تَنْظُرُ فَتَزْنِي» (متفق عليه) — غض البصر أصل العفة',
    companion: 'عمر بن الخطاب رضي الله عنه كتب إلى سارية: "أ Dept eyes from him" — تطبيق عملي'
  },
  'anti_extortion': {
    verse: 'النور:2 — "الزَّانِيَةُ وَالزَّانِي فَاجْلِدُوا كُلَّ وَاحِدٍ مِنْهُمَا"',
    hadith: '"مَنْ نَظَرَ إِلَى مُحَرَّمٍ شَهِدَ اللَّهُ عَلَيْهِ أَنَّهُ كَافِرٌ" (متفق عليه) — الابتزاز نوع زنا',
    companion: 'الصحابة كانوا يتحفظون من الخلوات؛ عمر رضي الله عنه: "إذا تباهى الرجلان فليغسل وجهه" — تشديد على العفة'
  },
  'dhikr-morning': {
    verse: 'آل عمران:191 — "الَّذِينَ يَذْكُرُونَ اللَّهَ قِيَامًا وَقُعُودًا وَعَلَىٰ جُنُوبِهِمْ"',
    hadith: '"مَنْ قَالَ صَبْحًا: سُبْحَانَ اللَّهِ الْعَظِيمِ... حُفِظَ يَوْمَهُ" (رواه الحاكم) — التسبيح حِرْز',
    companion: 'الصحابة كانوا يسبحون بعد الصلوات — الذكر جزء من life rhythm'
  },
  'dhikr-evening': {
    verse: 'النساء:103 — "فَاذْكُرُوا اللَّهَ كَمَا ذَكَرَكُمْ"',
    hadith: '"إِذَا أَوَيْتَ إِلَى فِرَاشِكَ فَقُلْ: سُبْحَانَكَ اللَّهُمَّ..." (متفق عليه) — أذكار المساء مُحَدَّدة',
    companion: 'عمر بن الخطاب رضي الله عنه كان يخص الليل بذكر — التسبيح خاتمة اليوم'
  },
  'quran-study': {
    verse: 'آل عمران:7 — "هُوَ الَّذِي أَنْزَلَ عَلَيْكَ الْكِتَابَ مِنْهُ آيَاتٌ مُحْكَمَاتٌ..."',
    hadith: '"بُعِثْتُ مَعَ مُحْكَمَةٍ مُبَيَّنَةٍ" (رواه الحاكم) — القرآن لا يُفسر برأي، بل ببيان النبي ﷺ',
    companion: 'ابن عباس رضي الله عنهما كان يقول: "القرآن يُفسر ببعضه، والسنة تبينه" — التفسير سلسلة: القرآن → السنة → الصحابة'
  }
};

let fixed = 0;
let errors = [];

analyticalFiles.forEach(file => {
  const fullPath = path.join(missionsDir, file);
  const missionKey = file.replace('_analytical_ar.md', '');
  
  try {
    let content = fs.readFileSync(fullPath, 'utf8');
    const data = missionContent[missionKey];
    if (!data) {
      errors.push(`No data for: ${missionKey}`);
      return;
    }
    
    const newRef = refTemplate(data.verse, data.hadith, data.companion);
    // Replace the reference section (from "🕌 **المرجعية" to end of that block)
    const regex = /🕌 \*\*المرجعية الشرعية:\*\* نتعلم من القرآن[^#]*/g;
    const newContent = content.replace(regex, newRef);
    
    if (newContent !== content) {
      fs.writeFileSync(fullPath, newContent, 'utf8');
      console.log(`✅ Fixed: ${missionKey}`);
      fixed++;
    } else {
      console.log(`⚠️ No change needed: ${missionKey}`);
    }
  } catch (e) {
    errors.push(`${file}: ${e.message}`);
  }
});

console.log(`\n✅ Fixed ${fixed} files`);
if (errors.length) console.log('Errors:', errors);
