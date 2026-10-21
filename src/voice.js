export const CHILEAN_VOICES={
 sabina:{name:'Catalina',locale:'es-CL',fallback:'Sabina'},
 victor:{name:'Lorenzo',locale:'es-CL',fallback:'Raúl'}
};

const spanish=voice=>(voice.lang||'').toLowerCase().startsWith('es');
const microsoft=voice=>/^Microsoft/i.test(voice.name||'');

export function selectVoice(voices,{voiceURI='',coach='sabina'}={}){
 const available=Array.from(voices||[]);
 const selected=available.find(voice=>voice.voiceURI===voiceURI);
 if(selected)return selected;
 const preferred=coach==='victor'
  ?[/lorenzo/i,/raul/i,/pablo/i,/jorge/i]
  :[/catalina/i,/sabina/i,/elvira/i,/dalia/i];
 for(const pattern of preferred){
  const found=available.find(voice=>microsoft(voice)&&spanish(voice)&&pattern.test(voice.name));
  if(found)return found;
 }
 return available.find(voice=>microsoft(voice)&&(voice.lang||'').toLowerCase()==='es-cl')
  ||available.find(voice=>microsoft(voice)&&spanish(voice))
  ||available.find(spanish);
}

export function speakText(text,{voiceURI='',coach='sabina',rate=.88}={}){
 if(!('speechSynthesis'in window))return false;
 speechSynthesis.cancel();
 const utterance=new SpeechSynthesisUtterance(text);
 const selected=selectVoice(speechSynthesis.getVoices(),{voiceURI,coach});
 if(selected)utterance.voice=selected;
 utterance.lang=selected?.lang||'es-CL';
 utterance.rate=rate;
 utterance.pitch=1;
 speechSynthesis.speak(utterance);
 return true;
}