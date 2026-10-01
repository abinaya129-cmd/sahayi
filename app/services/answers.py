"""General answers: government schemes BEYOND the 7 application flows.

SAHAYI's scope is 7 schemes she can fully process. But real users ask about
e-bikes, phones, scholarships, pensions. A dead-end "samajh nahi aaya" kills
trust - so SAHAYI answers honestly (with official sources) and steers back.
Every entry is bilingual (hi/en) and carries a rich card for the dashboard.

Honesty rule: if we don't know, SAHAYI says so and never invents a scheme.
"""
from ..nlu import _best

# key -> knowledge entry
KB = {
    "ebike": {
        "emoji": "🛵", "title": "PM E-DRIVE (Electric Vehicle)",
        "keywords": ["ebike", "e bike", "e-bike", "electric", "scooter", "ev",
                     "bike chahiye", "इलेक्ट्रिक", "स्कूटर", "गाड़ी battery"],
        "answer_hi": ("Electric bike par sarkar subsidy deti hai - PM E-DRIVE yojana. "
                      "E-scooter/bike par approx Rs 5,000 (model ke hisaab se Rs 10,000 tak), "
                      "e-rickshaw par Rs 25,000 tak. Kharidte waqt registered EV dealer par "
                      "Aadhaar se apply kariye - subsidy seedha price mein kat jaati hai."),
        "answer_en": ("Yes - the PM E-DRIVE scheme subsidises electric vehicles: about "
                      "Rs 5,000 on an e-scooter/e-bike (up to Rs 10,000 by model), up to "
                      "Rs 25,000 on e-rickshaws. Buy from a registered EV dealer with your "
                      "Aadhaar - the subsidy is deducted directly from the price."),
        "facts_hi": ["E-2W: approx Rs 5,000 subsidy", "E-rickshaw: Rs 25,000 tak",
                     "Subsidy dealer par hi price se cut jaati hai",
                     "Zaroori: Aadhaar, registered EV dealer"],
        "facts_en": ["E-2W: about Rs 5,000 subsidy", "E-rickshaw: up to Rs 25,000",
                     "Subsidy is deducted at the dealer itself",
                     "Needed: Aadhaar, registered EV dealer"],
        "source": "pmedrive.heavyindustry.gov.in",
    },
    "phone": {
        "emoji": "📱", "title": "Smartphone / Mobile",
        "keywords": ["phone", "mobile", "smartphone", "फोन", "मोबाइल", "cellphone"],
        "answer_hi": ("Free smartphone wali koi CENTRAL sarkari yojana abhi nahi hai - "
                      "jo bole wo galat hai, paisa mat dena. Kuch rajya apni local yojana "
                      "chalate hain (jaise Rajasthan/Madhya Pradesh) - apne Jan Suvidha "
                      "kendra ya collector office se poochein. Sasta 4G phone (Rs 999-1,500) "
                      "BSNL/Jio Bharat mein mil jaata hai."),
        "answer_en": ("There is NO central government scheme giving free smartphones - "
                      "anyone claiming so may be a scammer; do not pay money. A few states "
                      "(Rajasthan, Madhya Pradesh) run local phone schemes - ask at your "
                      "Jan Suvidha Kendra. Budget 4G phones (Rs 999-1,500) exist under "
                      "BSNL/Jio Bharat."),
        "facts_hi": ["Central free phone yojana: NAHI hai", "Kuch rajya local yojana dete hain",
                     "Scam se savdhan - OTP/paisa kabhi nahi", "Sasta 4G: Rs 999 se"],
        "facts_en": ["No central free-phone scheme exists", "Some states run local schemes",
                     "Beware of scams - never share OTP", "Budget 4G from Rs 999"],
        "source": "district collector office / CSC",
    },
    "scholarship": {
        "emoji": "🎓", "title": "National Scholarship Portal",
        "keywords": ["scholarship", "scholar", "छात्रवृत्ति", "padhai fees", "school fees",
                     "படிப்பு", "stud"],
        "answer_hi": ("Scholarship ke liye National Scholarship Portal (scholarships.gov.in) "
                      "hai: pre-matric (class 9-10) aur post-matric (11 se aage) - Rs 6,000 se "
                      "Rs 12,000/saal tak caste/income ke hisaab se. PM YASASVI OBC/EBC "
                      "students ke liye alag hai. Documents: Aadhaar, income certificate, "
                      "marks sheet, bank passbook."),
        "answer_en": ("Scholarships run through the National Scholarship Portal "
                      "(scholarships.gov.in): pre-matric (class 9-10) and post-matric "
                      "(class 11+) worth Rs 6,000-12,000/year depending on category and "
                      "income. PM YASASVI covers OBC/EBC students separately. Documents: "
                      "Aadhaar, income certificate, mark sheet, bank passbook."),
        "facts_hi": ["Pre-matric: class 9-10", "Post-matric: class 11 se aage",
                     "Rs 6,000-12,000/saal", "Apply: scholarships.gov.in (CSC madad karega)"],
        "facts_en": ["Pre-matric: class 9-10", "Post-matric: class 11 onwards",
                     "Rs 6,000-12,000/year", "Apply: scholarships.gov.in (CSC can help)"],
        "source": "scholarships.gov.in",
    },
    "pension": {
        "emoji": "👴", "title": "Atal Pension (APY) / Old-Age Pension",
        "keywords": ["pension", "पेंशन", "budhapa", "बुढ़ापा", "old age", "widow", "विधवा"],
        "answer_hi": ("Atal Pension Yojana (APY): 18-40 ki umar mein bank khata kholiye, "
                      "Rs 210/month se shuru - 60 ke baad Rs 1,000 se Rs 5,000/month pension "
                      "zindagi bhar. Widya/old-age pension (NSAP) ke liye apne block office "
                      "ya CSC se apply hota hai. Bank branch mein APY form bhariye."),
        "answer_en": ("Atal Pension Yojana (APY): open a bank account between age 18-40, "
                      "contribute from Rs 210/month, and receive Rs 1,000-5,000/month "
                      "pension for life after 60. Widow/old-age pension (NSAP) is applied "
                      "for at your block office or CSC."),
        "facts_hi": ["APY: Rs 210/month se", "60 ke baad Rs 1,000-5,000/month",
                     "NSAP widow/old-age: block office se", "Zaroori: Aadhaar, bank khata"],
        "facts_en": ["APY: from Rs 210/month", "After 60: Rs 1,000-5,000/month",
                     "NSAP widow/old-age: via block office", "Needed: Aadhaar, bank account"],
        "source": "npscra.nsdl.co.in / bank branch",
    },
    "solar": {
        "emoji": "☀️", "title": "PM Surya Ghar (Free Electricity)",
        "keywords": ["solar", "सोलर", "bijli", "electricity", "बिजली", "rooftop", "light bill"],
        "answer_hi": ("PM Surya Ghar Muft Bijli Yojana: ghar ki chhat par solar lagwaiye - "
                      "Rs 30,000 se Rs 78,000 tak subsidy, aur har mahine 300 unit tak bijli "
                      "MUFT. Registration pmsuryaghar.gov.in par ya CSC se. Pehle electricity "
                      "connection apne naam hona chahiye."),
        "answer_en": ("PM Surya Ghar Muft Bijli Yojana: install rooftop solar and get a "
                      "subsidy of Rs 30,000-78,000 plus up to 300 units of FREE electricity "
                      "every month. Register at pmsuryaghar.gov.in or via a CSC. The "
                      "electricity connection must be in your name first."),
        "facts_hi": ["Subsidy: Rs 30,000-78,000", "300 unit/month tak muft bijli",
                     "Apply: pmsuryaghar.gov.in ya CSC", "Connection aapke naam hona chahiye"],
        "facts_en": ["Subsidy: Rs 30,000-78,000", "Up to 300 free units/month",
                     "Apply: pmsuryaghar.gov.in or CSC", "Connection must be in your name"],
        "source": "pmsuryaghar.gov.in",
    },
    "ayushman": {
        "emoji": "🏥", "title": "Ayushman Bharat (PM-JAY)",
        "keywords": ["ayushman", "ayush", "hospital", "ilaj", "इलाज", "bima", "insurance",
                     "health", "स्वास्थ्य", "operation"],
        "answer_hi": ("Ayushman Bharat (PM-JAY): har saal Rs 5 LAKH tak ka free ilaaj - "
                      "operation, hospital sab cover. Check kariye ki aapka naam SECC/BPL "
                      "list mein hai: pmjay.gov.in par ya CSC se Ayushman card banwaiye. "
                      "Iske liye koi paisa NAHI lagta - jo maange wo fraud hai."),
        "answer_en": ("Ayushman Bharat (PM-JAY): FREE medical treatment worth up to Rs 5 "
                      "lakh every year - operations and hospitalisation covered. Check if "
                      "your name is on the SECC/BPL list and make your Ayushman card at "
                      "pmjay.gov.in or any CSC. It costs NOTHING - anyone asking money is a fraud."),
        "facts_hi": ["Rs 5 lakh/saal free ilaaj", "Card CSC par ban jaata hai",
                     "Koi fees nahi - fees maangne wala fraud hai", "Check: pmjay.gov.in"],
        "facts_en": ["Rs 5 lakh/year free treatment", "Card made at any CSC",
                     "No fees - fee-seekers are frauds", "Check: pmjay.gov.in"],
        "source": "pmjay.gov.in",
    },
    "drone": {
        "emoji": "🚁", "title": "Namo Drone Didi (Women SHG)",
        "keywords": ["drone", "ड्रोन", "didi drone", "shg", "mahila sangh"],
        "answer_hi": ("Namo Drone Didi: mahila SHG (self-help group) ko drone khareedne aur "
                      "training ke liye Rs 8 LAKH tak ki madad - drone se kheti ki nigraani aur "
                      "spraying ka business shuru hota hai. Apne SHG ke block office se "
                      "application kariye."),
        "answer_en": ("Namo Drone Didi: women's self-help groups (SHGs) get up to Rs 8 "
                      "lakh to buy agricultural drones with training - starting a crop "
                      "monitoring and spraying business. Apply through your SHG at the "
                      "block office."),
        "facts_hi": ["SHG ke liye: Rs 8 lakh tak", "Drone + training include",
                     "Block office se apply", "SHG member hona zaroori"],
        "facts_en": ["For SHGs: up to Rs 8 lakh", "Drone + training included",
                     "Apply via block office", "Must be an SHG member"],
        "source": "agri-infotech.gov.in / block office",
    },
    "mudra": {
        "emoji": "💼", "title": "Mudra / Stand Up India (Business Loan)",
        "keywords": ["loan", "mudra", "karz", "लोन", "कर्ज़", "business", "startup",
                     "dhandha", "dukaan"],
        "answer_hi": ("Apna kaam shuru karne ke liye: Mudra loan Rs 50,000 (Shishu) se "
                      "Rs 10 LAKH (Tarun) tak - BINA GUARANTOR, kisi se paise nahi lagte. "
                      "Women entrepreneurs ke liye Stand Up India Rs 1 CRORE tak deta hai. "
                      "Kisi bhi bank branch se business plan ke saath apply kariye. Loan ke "
                      "naam par advance maangne wala fraud hai."),
        "answer_en": ("To start your own work: a Mudra loan of Rs 50,000 (Shishu) up to "
                      "Rs 10 LAKH (Tarun) - NO guarantor, no agents. Women entrepreneurs can "
                      "get up to Rs 1 CRORE under Stand Up India. Apply at any bank branch "
                      "with a simple business plan. Anyone asking advance money for a loan is a fraud."),
        "facts_hi": ["Mudra: Rs 50,000-10 lakh, no guarantor", "Stand Up India: Rs 1 crore tak (women)",
                     "Bank branch se seedha apply", "Advance maangne wala fraud hai"],
        "facts_en": ["Mudra: Rs 50,000-10 lakh, no guarantor", "Stand Up India: up to Rs 1 crore (women)",
                     "Apply directly at a bank branch", "Advance-seekers are frauds"],
        "source": "mudra.org.in / bank branch",
    },
}

# ---------------------------------------------------------------- extra topics
# Real-life "she can ask anything" coverage: documents, day-to-day services,
# safety. Same bilingual format as the schemes above.
KB["aadhaar"] = {
    "emoji": "🆔", "title": "Aadhaar Card",
    "keywords": ["aadhaar", "adhar", "aadhar", "आधार", "uid", "aadhar card", "enrollment"],
    "answer_hi": ("Aadhaar banane/update karne ke liye najdiki Aadhaar Seva Kendra jaiye "
                  "(block office, post office ya CSC hota hai). Naya enrollment FREE hai; "
                  "update mein Rs 50 tak lag sakta hai. Documents: proof of identity + "
                  "address. Book kariye: appointments.uidai.gov.in"),
    "answer_en": ("To make or update an Aadhaar, go to the nearest Aadhaar Seva Kendra "
                  "(block office, post office or CSC). New enrolment is FREE; updates cost "
                  "up to Rs 50. Bring identity + address proof. Book at "
                  "appointments.uidai.gov.in"),
    "facts_hi": ["Naya Aadhaar: FREE", "Update: Rs 50 tak", "Zaroori: ID + address proof",
                 "Book: appointments.uidai.gov.in"],
    "facts_en": ["New enrolment: FREE", "Update: up to Rs 50", "Need: ID + address proof",
                 "Book: appointments.uidai.gov.in"],
    "source": "uidai.gov.in",
}
KB["ration"] = {
    "emoji": "🍚", "title": "Ration Card",
    "keywords": ["ration", "ration card", "राशन", "फूड", "food", "anna", "गेहूं",
                 "free grain", "anaj"],
    "answer_hi": ("Ration card se PM Garib Kalyan Yojana ke tahat HAR mahine muft anaj "
                  "milta hai (5 kg per person). Naya card ya naam jodne ke liye apne "
                  "taluk/tehsil food office jaiye - ya meraferd.rural.nic.in / apne rajya ke "
                  "portal par. Documents: Aadhaar, income certificate, address proof."),
    "answer_en": ("A ration card gets FREE grain every month under PM Garib Kalyan Yojana "
                  "(5 kg per person). For a new card or to add names, visit your taluk/tehsil "
                  "food office or your state's portal. Documents: Aadhaar, income "
                  "certificate, address proof."),
    "facts_hi": ["Muft anaj: 5 kg/person/month", "Apply: tehsil food office",
                 "Zaroori: Aadhaar, income certificate", "National portability bhi hai"],
    "facts_en": ["Free grain: 5 kg/person/month", "Apply: tehsil food office",
                 "Need: Aadhaar, income certificate", "National portability available"],
    "source": "nfsa.gov.in",
}
KB["pancard"] = {
    "emoji": "💳", "title": "PAN Card",
    "keywords": ["pan", "pan card", "पैन", "permanent account"],
    "answer_hi": ("PAN card ke liye e-filing portal (incometax.gov.in) ya NSDL/UTIITSL se "
                  "online apply hota hai - fees approx Rs 107 (physical card). Instant "
                  "e-PAN FREE hai, sirf Aadhaar se 10 minute mein! Link: onlineservices.nsdl.com"),
    "answer_en": ("Apply for a PAN card online at incometax.gov.in or via NSDL/UTIITSL - "
                  "fee about Rs 107 for a physical card. An instant FREE e-PAN takes just "
                  "10 minutes with only your Aadhaar!"),
    "facts_hi": ["Instant e-PAN: FREE, 10 minute", "Physical card: approx Rs 107",
                 "Sirf Aadhaar chahiye", "Apply: incometax.gov.in"],
    "facts_en": ["Instant e-PAN: FREE, 10 minutes", "Physical card: about Rs 107",
                 "Only Aadhaar needed", "Apply: incometax.gov.in"],
    "source": "incometax.gov.in",
}
KB["voterid"] = {
    "emoji": "🗳️", "title": "Voter ID",
    "keywords": ["voter", "vote", "वोट", "मतदाता", "election", "chunav"],
    "answer_hi": ("18 saal hue? Voter ID banwaiye: voters.eci.gov.in par Form 6 bhariye - "
                  "pura ONLINE, documents: Aadhaar, photo, address proof. Voting aapki sabse "
                  "badi shakti hai!"),
    "answer_en": ("Just turned 18? Get a Voter ID: fill Form 6 at voters.eci.gov.in - "
                  "fully ONLINE with Aadhaar, a photo and address proof. Voting is your "
                  "biggest power!"),
    "facts_hi": ["Form 6: naye voters ke liye", "Apply: voters.eci.gov.in",
                 "Documents: Aadhaar, photo, address", "Umur 18+ zaroori"],
    "facts_en": ["Form 6: for new voters", "Apply: voters.eci.gov.in",
                 "Need: Aadhaar, photo, address", "Must be 18+"],
    "source": "voters.eci.gov.in",
}
KB["passport"] = {
    "emoji": "🛂", "title": "Passport",
    "keywords": ["passport", "पासपोर्ट", "videsh", "abroad", "visa"],
    "answer_hi": ("Passport ke liye passportindia.gov.in par register karke appointment "
                  "liye - PSK (Passport Seva Kendra) jaiye. Normal: Rs 1,500 (10 saal), "
                  "60 din tak. Police verification hoti hai."),
    "answer_en": ("For a passport, register at passportindia.gov.in and book a PSK "
                  "(Passport Seva Kendra) appointment. Normal: Rs 1,500, valid 10 years, "
                  "delivered within about 60 days. Police verification is required."),
    "facts_hi": ["Fees: Rs 1,500 (normal)", "Valid: 10 saal", "Time: ~60 din",
                 "Book: passportindia.gov.in"],
    "facts_en": ["Fee: Rs 1,500 (normal)", "Valid: 10 years", "Time: ~60 days",
                 "Book: passportindia.gov.in"],
    "source": "passportindia.gov.in",
}
KB["kcc"] = {
    "emoji": "🚜", "title": "Kisan Credit Card (KCC)",
    "keywords": ["kcc", "credit card", "kisan credit", "kheti karz", "fasal karz", "मोटा कर्ज"],
    "answer_hi": ("Kisan Credit Card: kheti ke liye Rs 3 LAKH tak ka loan sirf 4% interest "
                  "par (7% - 3% prompt repayment discount)! Kisi bhi bank se Aadhaar, "
                  "zameen ke kagzat ke saath apply kariye."),
    "answer_en": ("Kisan Credit Card: crop loans up to Rs 3 LAKH at just 4% interest "
                  "(7% minus 3% prompt-repayment discount)! Apply at any bank with Aadhaar "
                  "and land documents."),
    "facts_hi": ["Rs 3 lakh tak loan", "Interest sirf 4%", "Kisi bhi bank se",
                 "Zaroori: Aadhaar, land record"],
    "facts_en": ["Loan up to Rs 3 lakh", "Interest only 4%", "At any bank",
                 "Need: Aadhaar, land record"],
    "source": "psc.barc.gov.in / bank branch",
}
KB["pmfby"] = {
    "emoji": "🌦️", "title": " Fasal Bima (PMFBY) - Crop Insurance",
    "keywords": ["fasal", "bima", "insurance crop", "सूखा", "sukha", "baadh", "barish",
                 "crop loss", "mausam"],
    "answer_hi": ("Fasal Bima Yojana (PMFBY): sukhne, baadh ya keet patang se fasal barbadi "
                  "par BEEMA. Kisan ka premium sirf 1.5-2% hai, baaki sarkar deti hai. Apne "
                  "bank/CSC ya pmfby.gov.in par apply kariye - fasal bohte samay."),
    "answer_en": ("Crop insurance (PMFBY): covers crop loss from drought, flood or pests. "
                  "Farmer pays only 1.5-2% premium; the government pays the rest. Apply at "
                  "your bank/CSC or pmfby.gov.in during sowing season."),
    "facts_hi": ["Kisan premium: sirf 1.5-2%", "Sukha/baad/keet sab cover",
                 "Apply: pmfby.gov.in ya CSC", "Boai ke season mein kariye"],
    "facts_en": ["Farmer premium: only 1.5-2%", "Drought, flood, pests all covered",
                 "Apply: pmfby.gov.in or CSC", "Do it in the sowing season"],
    "source": "pmfby.gov.in",
}
KB["soil"] = {
    "emoji": "🧪", "title": "Soil Health Card",
    "keywords": ["soil", "mitti", "मिट्टी", "khaad", "fertilizer", "urvarak"],
    "answer_hi": ("Soil Health Card: apni zameen ki mitti ki JANCH muft karaiye - pata "
                  "chalega kaunsa khaad kitna daalna hai. Apne gram sevak ya agriculture "
                  "office se sample karwaiye. Isse khaad ka kharcha 10% tak kam hota hai."),
    "answer_en": ("Soil Health Card: get your soil tested FREE - it tells you exactly how "
                  "much fertilizer to use, cutting costs by up to 10%. Ask your gram sevak "
                  "or agriculture office to take a sample."),
    "facts_hi": ["Mitti jaanch: FREE", "Khaad kharcha ~10% kam", "Gram sevak se sampark",
                 "Har 2 saal mein naya card"],
    "facts_en": ["Soil test: FREE", "Cuts fertiliser cost ~10%", "Contact your gram sevak",
                 "New card every 2 years"],
    "source": "soilhealth.dac.gov.in",
}
KB["epass"] = {
    "emoji": "🚌", "title": "Free Bus Travel for Women",
    "keywords": ["bus", "bás", "सफर", "safar", "travel free", "yatra", "stree sawari"],
    "answer_hi": ("Kayi rajyon mein mahilao ke liye FREE bus sawari hai: Karnataka (Shakti - "
                  "4 lac route), Telangana (MRTC), Tamil Nadu (city buses), Punjab, Delhi "
                  "(DTC). Bas confirm kariye ki aapke rajya mein hai - conductor ko boliye."),
    "answer_en": ("Several states give women FREE bus travel: Karnataka (Shakti scheme), "
                  "Telangana, Tamil Nadu (city buses), Punjab, Delhi (DTC). Just ask the "
                  "conductor whether your state runs it."),
    "facts_hi": ["Karnataka: Shakti yojana", "TN: city buses muft", "Delhi: DTC muft",
                 "Apne rajya mein confirm kariye"],
    "facts_en": ["Karnataka: Shakti scheme", "TN: free city buses", "Delhi: free DTC",
                 "Check your own state"],
    "source": "apne rajya ka transport department",
}
KB["helpline"] = {
    "emoji": "🆘", "title": "Emergency Helplines",
    "keywords": ["helpline", "emergency", "police", "ambulance", "bachao", "मदद karo",
                 "112", "1098", "181", "danger", "khatra", "pitai", "pareshan"],
    "answer_hi": ("SABHI emergency ke liye 112 (police/ambulance/fire). Mahila utpeeda: "
                  "181 (24x7, har bhasha mein). Bachche ke liye 1098. Garbh sambandhi: "
                  "104. Bilkul FREE hain - SAHAYI hamesha aapke saath hai."),
    "answer_en": ("For ALL emergencies call 112 (police/ambulance/fire). Women in danger: "
                  "181 (24x7, every language). Child help: 1098. Health advice: 104. "
                  "All FREE - SAHAYI is always with you."),
    "facts_hi": ["112: police/ambulance/fire", "181: mahila suraksha 24x7",
                 "1098: bachche ki madad", "Sab calls FREE"],
    "facts_en": ["112: police/ambulance/fire", "181: women safety 24x7",
                 "1098: child help", "All calls FREE"],
    "source": "MHA / NCW / MWCD",
}
KB["cyber"] = {
    "emoji": "🛡️", "title": "Cyber Fraud (1930)",
    "keywords": ["cyber", "otp aya", "paisa kat gaya", "fraud hua", "dhoka", "scam", "1930",
                 "thagi"],
    "answer_hi": ("Paisa ya OTP theek ho gaya? FORAN 1930 par call kariye (cyber helpline) "
                  "ya cybercrime.gov.in par report kariye - pehle ghante mein report karne se "
                  "paisa RUK SAKTA hai. Bank ko bhi turant bataiye: 1800-123-XXXX (apna bank)."),
    "answer_en": ("Money or OTP stolen? IMMEDIATELY call 1930 (cyber helpline) or report at "
                  "cybercrime.gov.in - reporting within the first hour can FREEZE the stolen "
                  "money. Also tell your bank at once."),
    "facts_hi": ["1930: cyber helpline", "1 ghanta: paisa ruk sakta hai",
                 "Report: cybercrime.gov.in", "Bank ko turant bataiye"],
    "facts_en": ["1930: cyber helpline", "First hour can freeze the money",
                 "Report: cybercrime.gov.in", "Tell your bank immediately"],
    "source": "cybercrime.gov.in",
}
KB["cashtransfer"] = {
    "emoji": "💰", "title": "DBT - Paisa Seedha Bank Mein",
    "keywords": ["dbt", "paisa nahi aya", "kist", "installment", "seedha transfer",
                 "आधार लिंक", "aadhaar link"],
    "answer_hi": ("Sarkari paisa (KISAN ki kist, gas subsidy, pension) DBT se seedha bank "
                  "khate mein aata hai. Paisa nahi aya? 1) Aadhaar-bank LINK check kariye "
                  "(CSC par), 2) apna status dekhein: dbtbharat.gov.in, 3) CSC ya bank "
                  "branch mein shikayat kariye."),
    "answer_en": ("Government money (KISAN installments, gas subsidy, pension) comes via "
                  "DBT straight to your bank account. Missing? 1) Check your Aadhaar-bank "
                  "link at a CSC, 2) track status at dbtbharat.gov.in, 3) complain at the "
                  "CSC or bank branch."),
    "facts_hi": ["Status: dbtbharat.gov.in", "Aadhaar-bank link zaroori",
                 "CSC par check karwaiye", "Shikayat ka jawab 30 din mein"],
    "facts_en": ["Track: dbtbharat.gov.in", "Aadhaar-bank link required",
                 "Check at any CSC", "Complaints answered in 30 days"],
    "source": "dbtbharat.gov.in",
}

FALLBACK_HI = ("Yeh sawal mere verified topics ke daayre mein nahi hai - galat jaankari "
               "dena theek nahi hoga. Lekin in sab mein main PURI madad kar sakti hoon:")
FALLBACK_EN = ("That question is outside my 7 verified application schemes - I won't guess. "
               "But here is everything I CAN fully process for you:")

_CHIPS = ["kisan", "gas", "scholarship", "pension", "ayushman", "aadhaar",
          "ration", "helpline", "ebike", "mudra loan"]


# Question words are shared via languages.STOP_WORDS (single source of truth).

def match(text: str):
    """Return (key, entry, score) for the best KB match, or (None, None, 0.0).
    Keywords containing spaces ('aadhar card') match the joined phrase;
    single words match content tokens (stop words removed)."""
    from ..languages import content_tokens
    tokens = content_tokens(text)
    if not tokens:
        return None, None, 0.0
    joined = " ".join(tokens)
    best_key, best_score = None, 0.0
    for key, entry in KB.items():
        score = max(
            _best(kw, tokens if " " not in kw else [joined])
            for kw in entry["keywords"]
        )
        if score > best_score:
            best_key, best_score = key, score
    if best_score >= 0.62:
        return best_key, KB[best_key], best_score
    return None, None, best_score
    return None, None


def answer(key: str, lang: str = "hi") -> dict:
    """Build a bilingual reply + rich card for a KB entry."""
    entry = KB[key]
    en = lang == "en"
    text = entry["answer_en"] if en else entry["answer_hi"]
    facts = entry["facts_en"] if en else entry["facts_hi"]
    chips = [c for c in _CHIPS if c != key][:5]
    return {
        "text": f"{entry['emoji']} {text} (Source: {entry['source']})" if en
                else f"{entry['emoji']} {text} (Srot: {entry['source']})",
        "card": {"type": "info", "emoji": entry["emoji"], "title": entry["title"],
                 "facts": facts, "source": entry["source"]},
        "chips": chips,
    }


def fallback(lang: str = "hi") -> dict:
    en = lang == "en"
    return {
        "text": FALLBACK_EN if en else FALLBACK_HI,
        "card": {"type": "fallback", "emoji": "🤝",
                 "title": "SAHAYI can apply for you" if en else "SAHAYI in sab mein apply kar sakti hai",
                 "facts": ["PM-KISAN", "Jan Dhan", "Ujjwala", "Awas", "MGNREGA",
                           "Vishwakarma", "Skill India"] if en else
                          ["PM-KISAN (kisan)", "Jan Dhan (bank)", "Ujjwala (gas)",
                           "Awas (ghar)", "MGNREGA (kaam)", "Vishwakarma (karigar)",
                           "Skill India (training)"]},
        "chips": ["kisan", "ghar", "kaam", "scholarship", "pension"],
    }
