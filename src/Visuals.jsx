import React from 'react';

const characterFiles={
 march:'march.webp',
 squat:'squat.webp',
 wide:'wide.webp',
 chair:'chair.webp',
 wall:'wall.webp',
 bird:'bird.webp',
 knee:'knee.webp',
 chest:'chest.webp',
 back:'back.webp',
 calf:'calf.webp',
 core:'core.webp',
 tilt:'tilt.webp',
 cat:'cat.webp'
};

const characterLabels={
 march:'Marcha suave elevando una rodilla',
 squat:'Sentadilla con el pecho elevado',
 wide:'Sentadilla con postura amplia',
 chair:'Sentarse y levantarse de una silla',
 wall:'Flexión de brazos apoyada en la pared',
 bird:'Bird dog en cuatro apoyos',
 knee:'Flexión modificada con las rodillas apoyadas',
 chest:'Apertura suave de pecho',
 back:'Movilidad suave de espalda alta',
 calf:'Estiramiento de pantorrilla de pie',
 core:'Respiración y activación del abdomen profundo',
 tilt:'Inclinación pélvica suave',
 cat:'Basculación suave en cuatro apoyos'
};

export function ExerciseArt({type='march',animated=true,small=false}){
 const resolved=characterFiles[type]?type:'march';
 const source=import.meta.env.BASE_URL+(animated?'animations/'+resolved+'.gif':'characters/'+characterFiles[resolved]);
 return <img
  className={'exercise-art character-cutout '+(small?'small ':'')+(animated?'animated-avatar':'')}
  src={source}
  alt={characterLabels[resolved]}
  loading={small?'lazy':'eager'}
  decoding="async"
 />;
}

export function HeroArt(){return <div className="hero-art" aria-hidden="true"><svg className="room" viewBox="0 0 400 330"><circle cx="208" cy="158" r="130" fill="#FF8C42" opacity=".12"/><rect x="255" y="34" width="92" height="145" rx="46" fill="#FFFFFF" opacity=".8"/><path d="M300 36v143M256 105h90" stroke="#FF8C42" opacity=".25" strokeWidth="3"/><circle cx="319" cy="75" r="21" fill="#F9CA24" opacity=".6"/><path d="M23 286h353" stroke="#FF8C42" opacity=".3" strokeWidth="3"/><ellipse cx="198" cy="282" rx="107" ry="16" fill="#9B59B6" opacity=".18"/><rect x="44" y="245" width="39" height="42" rx="6" fill="#FF8C42"/><path d="M64 246v-91" stroke="#5A6070" strokeWidth="3"/><ellipse cx="48" cy="192" rx="13" ry="29" transform="rotate(-35 48 192)" fill="#4ECDC4"/><ellipse cx="79" cy="168" rx="13" ry="29" transform="rotate(35 79 168)" fill="#A8E063"/><ellipse cx="78" cy="219" rx="13" ry="28" transform="rotate(35 78 219)" fill="#4ECDC4"/><path d="M340 239l9-12m-9 12 15 2m-15-2-2-14" stroke="#9B59B6" strokeWidth="3" fill="none"/><circle cx="104" cy="74" r="6" fill="#FF6B9D"/><path d="M375 172h-12m6-6v12" stroke="#FF8C42" strokeWidth="3"/></svg><div className="hero-person"><ExerciseArt type="chest" animated={false}/></div><span className="floating-note">Un poco hoy. Mucho para ti. ✨</span></div>}

export function Garden({count=0}){return <svg viewBox="0 0 300 150" role="img" aria-label={count+' sesiones completadas en tu jardín'}><ellipse cx="150" cy="134" rx="98" ry="9" fill="#9B59B6" opacity=".1"/><path d="M132 111h36l-5 25h-26z" fill="#FF8C42"/><path d="M150 112V70" stroke="#5A6070" strokeWidth="3"/><ellipse cx="140" cy="85" rx="11" ry="21" transform="rotate(-40 140 85)" fill="#4ECDC4"/><ellipse cx="162" cy="70" rx="11" ry="21" transform="rotate(35 162 70)" fill="#A8E063"/>{count>=3&&<g><path d="M85 128V65" stroke="#5A6070" strokeWidth="3"/><ellipse cx="74" cy="91" rx="10" ry="21" transform="rotate(-40 74 91)" fill="#4ECDC4"/><circle cx="85" cy="58" r="17" fill="#FF6B9D"/><circle cx="85" cy="58" r="7" fill="#F9CA24"/></g>}{count>=7&&<g><path d="M213 128V47" stroke="#5A6070" strokeWidth="3"/><ellipse cx="224" cy="86" rx="12" ry="24" transform="rotate(35 224 86)" fill="#A8E063"/><circle cx="213" cy="42" r="20" fill="#9B59B6"/><circle cx="213" cy="42" r="8" fill="#F9CA24"/></g>}</svg>}
