# TRA NEXUS — Mfumo wa Kiakili wa Mapato (Demo Prototype v5)

Imeandaliwa na Mustafa Z. Mambe, Founder & CEO wa Cyber Salama TZ.

## Jinsi ya Kuendesha Kwenye Kompyuta Yako (Local)
```
pip install -r requirements.txt
python app.py
```
Kisha fungua: http://127.0.0.1:5000

## Nywila za Majaribio (Demo Only)

**Msimamizi wa TRA:**
- Namba ya Utambulisho: `TRA-ADMIN`
- Nenosiri: `Nexus@2026!`

**Mlipakodi:**
- Namba ya Utambulisho: `142-998-775`
- Nenosiri: `Kodi@2026!`

Au tumia kitufe cha "Jisajili" kuunda akaunti mpya ya majaribio (usajili unahifadhiwa kwenye kumbukumbu ya muda tu — unafutika mfumo unapoanzishwa upya).

## Maboresho ya Toleo la 4 (Jipya Zaidi)
1. **Usajili wa Mtumiaji Mpya:** Ukurasa wa Login sasa una kiungo cha "Jisajili" chenye fomu kamili (jina, uhusika, kitambulisho, nenosiri + uthibitisho).
2. **Kuficha/Kuonyesha Nywila:** Ikoni ya jicho (👁) kwenye kila uwanja wa nenosiri, kwenye Login na Usajili.
3. **Lugha Mbili (Kiswahili + English):** Kitufe cha SW/EN kinapatikana kwenye kila ukurasa; menyu, vichwa vya habari, fomu, na Msaidizi wa AI vyote vinabadilika lugha papo hapo.
4. **Credit Iliyosasishwa:** "Imeandaliwa na Mustafa Z. Mambe, Founder & CEO wa Cyber Salama TZ" inaonekana kwenye kurasa za Login/Usajili.
5. **Kumbukumbu za Ukaguzi Zilizoboreshwa:** Sasa zinaonyesha idadi ya usajili mpya wa mtandaoni (siku 7 zilizopita) na jumla ya watumiaji waliotumia mfumo, pamoja na kumbukumbu za kila mtu anayeingia (login log halisi).
6. **Msaidizi wa AI Aliyeongezwa Uwezo:** Zaidi ya maswali/majibu 15 ya sampuli (Kiswahili + English) kuhusu TIN, VAT, EFD, faini, migogoro, BRELA, GePG, n.k. Swali lisilo na jibu la moja kwa moja linatumwa moja kwa moja kwenye "Ukaguzi wa Maswali" kwa ajili ya Msimamizi.
7. **Sehemu Mpya ya Ukaguzi wa Maswali:** Tab mpya ya Admin inayoonyesha orodha ya maswali yaliyoshindwa kupata jibu la moja kwa moja, tayari kwa Msimamizi kuyapitia na kuboresha hifadhi ya majibu.
8. **Menyu za Pembeni Zinazofanya Kazi Kikamilifu:** Tabs zote (Dashibodi, Ugunduzi wa Soko, Msaidizi wa AI, Ukaguzi) zinabadilika papo hapo bila kupakia upya ukurasa.

## Maboresho ya Toleo la 5 (Jipya Zaidi)
1. **Taarifa Zinazobadilika kwa Kila Mlipakodi:** Kila akaunti mpya ya mlipakodi sasa inapata biashara/mkoa/kodi/risiti zake za kipekee (si data ile ile kwa kila mtu), na kodi/idadi ya risiti huongezeka kadri muda unavyopita tangu usajili.
2. **Usajili wenye OTP (Hali ya Demo):** Baada ya kujaza fomu, mtumiaji anaonyeshwa namba ya uthibitisho (kwa hali halisi ingetumwa SMS/Email) kabla ya kukamilisha usajili.
3. **Usajili wa Maafisa wa TRA Umetenganishwa:** Fomu ya umma ya "Jisajili" sasa ni kwa Walipakodi pekee. Maafisa wapya wa TRA wanasajiliwa na Admin aliyeshaingia, kupitia menyu "Sajili Afisa wa TRA".
4. **Akaunti Yangu:** Ukurasa mpya wa kubadili jina, barua pepe, namba ya simu, na nenosiri.
5. **Faragha ya Namba/TIN Zilizogundulika:** Namba za simu za wamiliki wa biashara zilizogundulika sasa zinaonekana zikiwa zimefichwa sehemu ya kati (mf. `071***78`). Admin/AI anaweza kuwasiliana nao moja kwa moja kupitia kitufe cha "Fungua WhatsApp" (ujumbe wa elimu au onyo) bila namba kamili kuonekana popote kwenye ukurasa.
6. **Ramani ya Ofisi za TRA:** Sehemu ya Msaidizi wa AI ina ramani ya Tanzania yenye alama za ofisi za kila mkoa (bonyeza kuona anwani/simu); mfumo pia unajibu moja kwa moja maswali kama "ofisi ya Mwanza iko wapi".
7. **Sauti (Voice Input):** Kitufe cha kipaza sauti (🎙) kwenye Msaidizi wa AI — kinatumia uwezo wa kivinjari cha Chrome kubadilisha sauti kuwa maneno na kutuma moja kwa moja.
8. **Enter Inatuma Ujumbe:** Kubonyeza Enter kwenye kisanduku cha mazungumzo sasa kunatuma ujumbe moja kwa moja.
9. **Mazungumzo Yanabaki Baada ya Kubadili Lugha:** Historia ya mazungumzo na AI Assistant haifutiki tena unapobadili SW/EN.
10. **Admin Anaweza Kujibu Maswali Moja kwa Moja:** Kwenye "Ukaguzi wa Maswali", Admin anaweza kuandika jibu ambalo (a) linatumwa moja kwa moja kwa aliyeuliza bila kufutika, na (b) linaongezwa kwenye hifadhi ya AI ili swali kama hilo lijibiwe moja kwa moja siku zijazo.
11. **Jina la Chatbot:** Sasa linaitwa "AI ASSISTANT" badala ya "AI" tu.
12. **Kupanga Login:** Uchaguzi wa "uhusika" (role) umeondolewa kwenye fomu ya Login — mfumo unatambua kiotomatiki kama ni Admin au Mlipakodi kutoka kwenye akaunti iliyosajiliwa, hivyo hakuna tena mkanganyiko.
13. **Kudumu kwa Taarifa (JSON File Persistence):** Taarifa za watumiaji, maswali, na mazungumzo sasa zinahifadhiwa kwenye faili `tra_nexus_state.json` karibu na app.py. Ukizima na kuwasha upya mfumo (hata kwenye CMD), taarifa hazitapotea tena. **KUMBUKA:** kwenye baadhi ya huduma za "free tier" mtandaoni (kama Render free plan), faili hii inaweza kufutika endapo huduma nzima itapangwa upya (full redeploy) — kwa uzalishaji halisi, tumia database ya kudumu (PostgreSQL).
14. **Malipo ya Lipa Sasa (GePG) - Onyesho:** Kitufe cha "Lipa Sasa" sasa kinafungua dirisha linaloonyesha Namba ya Udhibiti (Control Number) iliyotengenezwa papo hapo, uchaguzi wa mtandao wa simu, na uthibitisho wa malipo (muamala wa onyesho pekee).

## Muhimu Kabla ya Kuwasilisha kwa TRA
- Hii ni **prototype ya kuonyesha wazo (proof of concept)**, si mfumo tayari kutumika (production-ready).
- Data zote (majina ya kampuni, takwimu za mikoa, miamala, na namba/anwani za ofisi za TRA) ni za kubuni kwa madhumuni ya demo pekee — kila ukurasa huonyesha hilo wazi. Anwani/namba za ofisi za TRA zilizoonyeshwa kwenye ramani ni za MFANO na zinapaswa kubadilishwa na taarifa halisi za TRA kabla ya matumizi rasmi.
- OTP ya usajili ni ya "hali ya demo" (inaonyeshwa moja kwa moja ukurasani) kwa sababu kutuma SMS/Email halisi kunahitaji huduma ya kulipia (k.m. Twilio, SendGrid) ambayo haijaunganishwa kwenye demo hii.
- Voice Input inategemea uwezo wa kivinjari (Web Speech API) — inafanya kazi vizuri zaidi kwenye Google Chrome; huenda isifanye kazi kwenye baadhi ya vivinjari vingine.
- Usajili/taarifa sasa zinahifadhiwa kwenye faili la JSON (angalia #13 hapo juu) badala ya kumbukumbu ya muda pekee, lakini bado si mbadala kamili wa database ya uzalishaji.

## Jinsi ya Kuiweka Mtandaoni (Kupata Link ya Kudumu kwa Proposal)

Njia rahisi na ya bure kwa kiwango hiki cha demo ni **Render.com**:

1. Tengeneza akaunti bure kwenye https://render.com
2. Pakia faili hizi (app.py, requirements.txt, Procfile) kwenye GitHub repo mpya
3. Kwenye Render, chagua "New Web Service" → unganisha na repo hiyo
4. Render itagundua Procfile kiotomatiki na kuanzisha huduma
5. Ndani ya dakika chache utapata link ya kudumu kama `https://tra-nexus-demo.onrender.com`

Njia mbadala: **PythonAnywhere** (bure kwa miradi midogo) au **Railway.app** — zote zinafanya kazi vizuri na Flask bila mabadiliko ya ziada kwenye code hii.

Baada ya kupata link, iweke moja kwa moja kwenye Sehemu ya "Kuhusu Mtayarishaji" au kama Kiambatisho A ndani ya proposal yako.