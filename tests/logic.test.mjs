
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {buildPlan,defaults,GOALS,EXERCISES,DIASTASIS_SAFE,compatible,adaptation,makeRecord,readStore,writeStore,weekDays,localDay} from '../src/data.js';
test('Todas las combinaciones producen exactamente 10, 12 o 15 minutos y respetan exclusiones',()=>{
 for(const minutes of [10,12,15])for(const goal of Object.keys(GOALS))for(const level of ['new','returning','active'])for(let mask=0;mask<32;mask++)for(const equipment of [[],['chair']])for(const energy of ['normal','low'])for(const diastasis of [false,true]){
 const avoid=['floor','wrists','knees','back','shoulders'].filter((_,i)=>mask&(1<<i)),p={...defaults,minutes,goal,level,avoid,equipment,diastasis},plan=buildPlan(p,[],energy);
 assert.equal(plan.stages.reduce((s,x)=>s+x.seconds,0),minutes*60);
 assert.ok(plan.stages.every(st=>compatible(st.exercise,p)));
 assert.ok(plan.work>=15&&plan.work<=40);
 assert.ok(plan.stages.every(st=>st.seconds>0));
 if(diastasis){assert.ok(plan.stages.every(st=>DIASTASIS_SAFE.has(st.exercise.id)));assert.ok(plan.work<=20)}
 }});
test('La adaptación responde a esfuerzo, técnica y molestias',()=>{
 assert.equal(adaptation(defaults,[]).work,20);
 const easy={complete:true,effort:3,technique:'good',pain:false};
 assert.equal(adaptation(defaults,[easy,easy]).work,25);
 assert.equal(adaptation(defaults,[easy,{...easy,effort:9}]).work,15);
 assert.equal(adaptation(defaults,[easy,{...easy,technique:'hard'}]).mode,'ease');
 assert.equal(adaptation(defaults,[easy,{...easy,pain:true}]).mode,'care');
 assert.equal(adaptation(defaults,[{...easy,complete:false},easy]).work,20);
});
test('Omitir o finalizar antes no crea una sesión completa ni minutos ficticios',()=>{
 const plan=buildPlan(defaults),full=plan.stages.map(st=>({elapsed:st.seconds,kind:st.kind,exercise:st.exercise.id,full:true}));
 const feedback={effort:5,technique:'good',pain:false,notes:''};
 assert.equal(makeRecord({id:'1',plan,done:full},feedback).complete,true);
 assert.equal(makeRecord({id:'1',plan,done:full},feedback).seconds,720);
 const partial=[{...full[0],elapsed:3,full:false}];
 const r=makeRecord({id:'2',plan,done:partial},feedback);assert.equal(r.complete,false);assert.equal(r.seconds,3);assert.equal(r.skipped,1);
});
test('Persistencia y recuperación de sesión',()=>{
 let raw=null;const storage={getItem:()=>raw,setItem:(_,v)=>{raw=v}};
 assert.equal(readStore(storage).profile,null);raw='{bad';assert.equal(readStore(storage).profile,null);
 const plan=buildPlan(defaults),active={id:'draft',plan,index:1,elapsed:3,done:[]};writeStore({profile:defaults,sessions:[],active},storage);
 assert.equal(readStore(storage).active.index,1);assert.equal(readStore(storage).profile.minutes,12);
});
test('Calendario usa días locales y empieza en lunes',()=>{const d=new Date(2026,9,21,12);assert.equal(localDay(d),'2026-10-21');assert.equal(weekDays(d)[0].date,'2026-10-19');assert.equal(weekDays(d)[6].date,'2026-10-25')});
test('Cada ejercicio tiene GIF de Sabina y Víctor e instrucciones concretas',()=>{assert.equal(EXERCISES.length,21);for(const e of EXERCISES){assert.equal(e.steps.length,3);for(const coach of ['sabina','victor']){const gif=new URL('../public/animations/'+coach+'/'+e.type+'.gif',import.meta.url),still=new URL('../public/characters/'+coach+'/'+e.type+'.webp',import.meta.url);assert.ok(fs.statSync(gif).size>10000);assert.ok(fs.statSync(still).size>1000)}}});
test('El modo diástasis usa solo movimientos marcados como compatibles',()=>{const plan=buildPlan({...defaults,diastasis:true,level:'active'},[],'normal');assert.ok(plan.pool.length>=2);assert.ok(plan.pool.every(e=>DIASTASIS_SAFE.has(e.id)));assert.ok(!plan.pool.some(e=>['knee','squat','wide'].includes(e.id)));assert.ok(plan.pool.some(e=>e.id==='dead-bug'));assert.equal(plan.work,20)});
test('El enfoque de abdomen bajo activa cuidado de diástasis y rota la rutina',()=>{const profile={...defaults,goal:'core',diastasis:false,level:'active'},first=buildPlan(profile,[]),second=buildPlan(profile,[{complete:true}]);assert.ok(first.pool.every(e=>DIASTASIS_SAFE.has(e.id)));assert.ok(first.pool.some(e=>e.id==='heel-slide'));assert.ok(first.pool.some(e=>e.id==='supine-march'));assert.notDeepEqual(first.pool.map(e=>e.id),second.pool.map(e=>e.id));assert.equal(first.work,20)});

test('Las progresiones abdominales quedan fuera del nivel inicial',()=>{const plan=buildPlan({...defaults,goal:'core',diastasis:true,level:'new'},[]);assert.ok(!plan.pool.some(e=>e.progression));assert.ok(plan.pool.some(e=>e.id==='supine-march'))});
test('Las molestias nunca aumentan un intervalo previamente reducido',()=>{assert.equal(adaptation(defaults,[{pain:true,work:15}]).work,15)});
