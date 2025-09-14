// quiz-data.js (4 subjects × 3 sets × 10 questions each)
// Structure: quizData[subject][set] = array of 10 questions { q, options[], ans }

const quizData = {
  math1: {
    1: [
      { q: "2 + 3 = ?", options:["4","5","6","7"], ans:"5" },
      { q: "7 - 4 = ?", options:["1","2","3","4"], ans:"3" },
      { q: "5 × 2 = ?", options:["7","8","9","10"], ans:"10" },
      { q: "12 ÷ 4 = ?", options:["2","3","4","6"], ans:"3" },
      { q: "Square root of 36?", options:["5","6","7","8"], ans:"6" },
      { q: "10 + 15 = ?", options:["20","23","25","27"], ans:"25" },
      { q: "9 − 3 = ?", options:["6","5","4","7"], ans:"6" },
      { q: "3 × 3 = ?", options:["6","7","8","9"], ans:"9" },
      { q: "18 ÷ 3 = ?", options:["5","6","7","8"], ans:"6" },
      { q: "What is 0 + 5?", options:["0","3","4","5"], ans:"5" }
    ],
    2: [
      { q: "4 + 6 = ?", options:["8","9","10","11"], ans:"10" },
      { q: "8 − 5 = ?", options:["2","3","4","5"], ans:"3" },
      { q: "6 × 3 = ?", options:["16","18","20","22"], ans:"18" },
      { q: "14 ÷ 2 = ?", options:["6","7","8","9"], ans:"7" },
      { q: "Square root of 49?", options:["6","7","8","9"], ans:"7" },
      { q: "7 + 7 = ?", options:["13","14","15","16"], ans:"14" },
      { q: "15 − 5 = ?", options:["8","9","10","11"], ans:"10" },
      { q: "2 × 8 = ?", options:["14","15","16","17"], ans:"16" },
      { q: "20 ÷ 5 = ?", options:["2","3","4","5"], ans:"4" },
      { q: "1 + 9 = ?", options:["9","10","11","12"], ans:"10" }
    ],
    3: [
      { q: "3 + 4 = ?", options:["6","7","8","9"], ans:"7" },
      { q: "11 − 2 = ?", options:["8","9","10","11"], ans:"9" },
      { q: "4 × 4 = ?", options:["12","14","15","16"], ans:"16" },
      { q: "24 ÷ 6 = ?", options:["2","3","4","5"], ans:"4" },
      { q: "Square root of 25?", options:["4","5","6","7"], ans:"5" },
      { q: "9 + 6 = ?", options:["14","15","16","17"], ans:"15" },
      { q: "8 − 3 = ?", options:["4","5","6","7"], ans:"5" },
      { q: "5 × 5 = ?", options:["20","22","24","25"], ans:"25" },
      { q: "30 ÷ 6 = ?", options:["4","5","6","7"], ans:"5" },
      { q: "0 + 8 = ?", options:["6","7","8","9"], ans:"8" }
    ]
  },

  math2: {
    1: [
      { q:"Solve: 2x = 8. x = ?", options:["2","3","4","5"], ans:"4" },
      { q:"If x=3, then 3x+2 = ?", options:["8","9","10","11"], ans:"11" },
      { q:"HCF of 6 and 9?", options:["2","3","6","9"], ans:"3" },
      { q:"LCM of 4 and 6?", options:["8","10","12","14"], ans:"12" },
      { q:"5^2 = ?", options:["10","20","25","30"], ans:"25" },
      { q:"20% of 200 = ?", options:["20","30","40","50"], ans:"40" },
      { q:"Which is a prime? 9 or 11?", options:["9","10","11","12"], ans:"11" },
      { q:"Solve: x + 5 = 12 => x = ?", options:["6","7","8","9"], ans:"7" },
      { q:"If y=2, 2y+3 = ?", options:["6","7","8","9"], ans:"7" },
      { q:"10×(2+3) = ?", options:["20","40","50","60"], ans:"50" }
    ],
    2: [
      { q:"Simplify: 3(2+4) = ?", options:["12","14","16","18"], ans:"18" },
      { q:"Find x: 5x=25 => x=?", options:["4","5","6","7"], ans:"5" },
      { q:"What is 7×7?", options:["42","45","48","49"], ans:"49" },
      { q:"Percentage: 50% of 80 = ?", options:["30","40","50","60"], ans:"40" },
      { q:"Square root of 81?", options:["8","9","10","11"], ans:"9" },
      { q:"LCM of 3 and 5?", options:["8","10","12","15"], ans:"15" },
      { q:"2^3 = ?", options:["6","7","8","9"], ans:"8" },
      { q:"9+9+9 = ?", options:["18","27","36","45"], ans:"27" },
      { q:"15 ÷ 3 = ?", options:["3","4","5","6"], ans:"5" },
      { q:"If a=2, 2a+1=?", options:["4","5","6","7"], ans:"5" }
    ],
    3: [
      { q:"Solve: x-4=6 => x=?", options:["8","9","10","11"], ans:"10" },
      { q:"5+5×2 = ?", options:["15","20","25","30"], ans:"15" },
      { q:"HCF of 10 and 15?", options:["3","4","5","6"], ans:"5" },
      { q:"LCM of 2 and 7?", options:["7","14","21","28"], ans:"14" },
      { q:"10^2 = ?", options:["100","200","1000","10"], ans:"100" },
      { q:"20% of 50 = ?", options:["5","10","15","20"], ans:"10" },
      { q:"Prime between 10 and 20?", options:["12","13","14","15"], ans:"13" },
      { q:"Solve: 3x=12 => x=?", options:["3","4","5","6"], ans:"4" },
      { q:"8×4 = ?", options:["24","28","32","36"], ans:"32" },
      { q:"6+7 = ?", options:["11","12","13","14"], ans:"13" }
    ]
  },

  english: {
    1: [
      { q:"Synonym of 'Happy'?", options:["Sad","Angry","Joyful","Tired"], ans:"Joyful" },
      { q:"Antonym of 'Big'?", options:["Large","Huge","Small","Tall"], ans:"Small" },
      { q:"Fill: She ___ reading.", options:["is","are","am","be"], ans:"is" },
      { q:"Choose: 'Their' vs 'There' -> '___ house is big.'", options:["Their","There","They're","The"], ans:"Their" },
      { q:"Plural of 'Child'?", options:["Childs","Children","Childes","Child"], ans:"Children" },
      { q:"Past tense of 'Go'?", options:["Goed","Went","Go","Gone"], ans:"Went" },
      { q:"Pronoun for 'Sangeeta' is?", options:["He","She","They","It"], ans:"She" },
      { q:"Pick adjective: 'A ___ day'", options:["sun","sunny","sunned","sunning"], ans:"sunny" },
      { q:"Fill: He ___ a book yesterday.", options:["reads","read","will read","reading"], ans:"read" },
      { q:"Opposite of 'Fast'?", options:["Quick","Rapid","Slow","Swift"], ans:"Slow" }
    ],
    2: [
      { q:"Synonym of 'Small'?", options:["Tiny","Huge","Large","Big"], ans:"Tiny" },
      { q:"Antonym of 'Happy'?", options:["Sad","Glad","Joyful","Merry"], ans:"Sad" },
      { q:"Fill: They ___ playing.", options:["is","are","am","be"], ans:"are" },
      { q:"Choose: 'It's' vs 'Its' -> '___ raining.'", options:["Its","It's","Itts","It is"], ans:"It's" },
      { q:"Plural of 'Box'?", options:["Boxs","Boxes","Boxen","Boxes"], ans:"Boxes" },
      { q:"Past of 'Take'?", options:["Took","Taken","Take","Takes"], ans:"Took" },
      { q:"Pronoun for group is?", options:["He","She","They","It"], ans:"They" },
      { q:"Adjective: 'a ___ girl'", options:["beauty","beautiful","beautified","beautifies"], ans:"beautiful" },
      { q:"Fill: I ___ seen him.", options:["have","has","had","having"], ans:"have" },
      { q:"Opposite of 'Cold'?", options:["Hot","Cool","Warm","Freezing"], ans:"Hot" }
    ],
    3: [
      { q:"Synonym of 'Begin'?", options:["Start","Stop","End","Finish"], ans:"Start" },
      { q:"Antonym of 'Cheap'?", options:["Affordable","Expensive","Low","Bargain"], ans:"Expensive" },
      { q:"Fill: She ___ to school every day.", options:["go","goes","going","went"], ans:"goes" },
      { q:"Correct spelling: 'Receive' or 'Recieve'?", options:["Receive","Recieve","Recive","Receeve"], ans:"Receive" },
      { q:"Plural of 'Mouse'?", options:["Mouses","Mice","Mouse","Mices"], ans:"Mice" },
      { q:"Past of 'Sing'?", options:["Sang","Singed","Sung","Sings"], ans:"Sang" },
      { q:"Pronoun for 'the teacher'?", options:["He","She","They","It"], ans:"She" },
      { q:"Pick adverb: 'She runs ___'", options:["Quick","Quickly","Quicker","Quickest"], ans:"Quickly" },
      { q:"Fill: They ___ dinner now.", options:["eat","eating","are eating","eats"], ans:"are eating" },
      { q:"Opposite of 'Light'?", options:["Heavy","Bright","Soft","Dim"], ans:"Heavy" }
    ]
  },

  geography: {
    1: [
      { q:"Capital of India?", options:["Mumbai","New Delhi","Kolkata","Chennai"], ans:"New Delhi" },
      { q:"Largest continent?", options:["Asia","Africa","Europe","Antarctica"], ans:"Asia" },
      { q:"River Ganga originates from?", options:["Gangotri","Yamunotri","Haridwar","Rishikesh"], ans:"Gangotri" },
      { q:"Highest mountain in world?", options:["K2","Everest","Kangchenjunga","Lhotse"], ans:"Everest" },
      { q:"Largest ocean?", options:["Indian","Atlantic","Pacific","Arctic"], ans:"Pacific" },
      { q:"Which country is a peninsula?", options:["India","Saudi Arabia","Japan","Canada"], ans:"Japan" },
      { q:"Capital of Maharashtra?", options:["Pune","Mumbai","Nagpur","Nashik"], ans:"Mumbai" },
      { q:"Which is a desert?", options:["Sahara","Amazon","Ganges","Nile"], ans:"Sahara" },
      { q:"Which is an island nation?", options:["Nepal","Sri Lanka","Bhutan","Bangladesh"], ans:"Sri Lanka" },
      { q:"Longest river in India?", options:["Godavari","Ganga","Narmada","Brahmaputra"], ans:"Ganga" }
    ],
    2: [
      { q:"Which ocean lies to the west of India?", options:["Pacific","Atlantic","Indian","Arctic"], ans:"Indian" },
      { q:"Capital of Australia?", options:["Sydney","Melbourne","Canberra","Perth"], ans:"Canberra" },
      { q:"Which country is largest by area?", options:["Russia","China","USA","India"], ans:"Russia" },
      { q:"Equator passes through which continent?", options:["Asia","Africa","Europe","Australia"], ans:"Africa" },
      { q:"Which sea is east of India?", options:["Arabian Sea","Bay of Bengal","Red Sea","Mediterranean"], ans:"Bay of Bengal" },
      { q:"Capital of UK?", options:["London","Manchester","Birmingham","Edinburgh"], ans:"London" },
      { q:"Which is the smallest continent?", options:["Australia","Europe","Antarctica","South America"], ans:"Australia" },
      { q:"Name of ring of volcanoes region?", options:["Ring of Fire","Ring of Earth","Volcano Belt","Fire Circle"], ans:"Ring of Fire" },
      { q:"Which country has largest population?", options:["India","China","USA","Indonesia"], ans:"China" },
      { q:"Which river flows through Cairo?", options:["Nile","Amazon","Ganga","Yangtze"], ans:"Nile" }
    ],
    3: [
      { q:"Which mountain range is in India?", options:["Himalaya","Andes","Alps","Rockies"], ans:"Himalaya" },
      { q:"Which desert is in India?", options:["Thar","Sahara","Gobi","Kalahari"], ans:"Thar" },
      { q:"Capital of Japan?", options:["Tokyo","Kyoto","Osaka","Nagoya"], ans:"Tokyo" },
      { q:"Largest state in India by area?", options:["Maharashtra","Rajasthan","UP","Madhya Pradesh"], ans:"Rajasthan" },
      { q:"Which is a tropical rainforest?", options:["Amazon","Sahara","Gobi","Kalahari"], ans:"Amazon" },
      { q:"Which gulf is near Mumbai?", options:["Gulf of Kutch","Gulf of Khambhat","Gulf of Mannar","Gulf of Aden"], ans:"Gulf of Khambhat" },
      { q:"Which of these is an archipelago?", options:["Japan","India","China","Nepal"], ans:"Japan" },
      { q:"Which river forms the Grand Canyon?", options:["Colorado","Mississippi","Amazon","Ganges"], ans:"Colorado" },
      { q:"Which is nearest to North Pole?", options:["Arctic Ocean","Indian Ocean","Atlantic Ocean","Pacific Ocean"], ans:"Arctic Ocean" },
      { q:"Which continent has most countries?", options:["Africa","Asia","Europe","South America"], ans:"Africa" }
    ]
  }
};
