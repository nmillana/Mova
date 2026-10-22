import {chromium,expect} from '@playwright/test';
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>m.type()==='error'&&errors.push(m.text()));
await page.goto('http://127.0.0.1:5178');
await page.evaluate(()=>localStorage.setItem('mova-personal-v1',JSON.stringify({version:1,profile:{name:'',goal:'habit',level:'active',minutes:12,days:3,equipment:[],avoid:[],diastasis:true,sound:true,voiceURI:'',coach:'sabina'},sessions:[],active:null})));
await page.reload();await page.getByRole('button',{name:'Ejercicios',exact:true}).click();await page.getByRole('checkbox').uncheck();
await expect(page.locator('.library-card')).toHaveCount(21);
const demonstrations=[
 ['Respiración y abdomen profundo','core'],['Deslizamiento de talón','heel-slide'],['Marcha supina','supine-march'],
 ['Dead bug modificado','dead-bug'],['Puente de glúteos','glute-bridge'],['Bird dog','bird'],
 ['Flexiones en pared','wall'],['Sentadilla','squat'],['Subida a escalón bajo','step-up'],
 ['Elevación de talones','calf-raise'],['Plancha lateral con rodillas','side-plank-knees']
];
for(const [name,type] of demonstrations){
 await page.getByRole('button',{name:new RegExp(name)}).first().click();
 const image=page.locator('.demo-media img');
 await expect(image).toHaveAttribute('src',new RegExp('animations/sabina/'+type+'\\.gif'));
 await expect.poll(()=>image.evaluate(i=>i.complete&&i.naturalWidth===420&&i.naturalHeight===420)).toBe(true);
 await expect(page.locator('body')).toHaveJSProperty('scrollWidth',390);
 await page.getByRole('button',{name:'Cerrar',exact:true}).click();
}
expect(errors).toEqual([]);
console.log(JSON.stringify({catalog:21,gifsChecked:demonstrations.length,noVideo:await page.locator('iframe').count()===0,mobileNoOverflow:true,errors}));
await browser.close();
