const { chromium }=require('playwright');
const fs=require('fs'),path=require('path');
const s=JSON.parse(fs.readFileSync(path.join(__dirname,'local-environment.json'))), fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'browser-fixture.json')));
const base=`http://127.0.0.1:${s.web_port}`,api=`http://127.0.0.1:${s.api_port}`;
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.setDefaultTimeout(20000);
 async function call(route,method='GET',body){return page.evaluate(async({url,method,body})=>{const r=await fetch(url,{method,credentials:'include',headers:{'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});return {status:r.status,body:await r.text()};},{url:api+route,method,body});}
 await page.goto(base+'/manage');await page.locator('#username').fill('ci-admin');await page.locator('#password').fill('ci-test-admin-password');await page.getByRole('button',{name:'密码登录',exact:true}).click();await page.getByRole('heading',{name:'管理面板',exact:true}).waitFor();
 console.log('AUTH cookie login succeeded');
 console.log('LEGACY_KP_DELETE',JSON.stringify(await call('/api/admin/knowledge-points/'+fixture.legacy_kp_id,'DELETE')));
 console.log('OCR_DISABLED_HTTP',JSON.stringify(await call('/api/admin/captures/'+fixture.capture_id+'/recognize','POST')));
 console.log('OCR_RETRY_HTTP',JSON.stringify(await call('/api/admin/captures/'+fixture.capture_id+'/recognize','POST')));
 await page.goto(base+'/manage/review');
 const card=page.getByRole('heading',{name:'VERIFY MULTIPLE CHOICE R01',exact:true}).locator('xpath=ancestor::div[contains(@class,"rounded-lg")][1]');
 await card.getByRole('button',{name:'再答',exact:true}).click();
 const a=card.getByRole('button',{name:'A. A option',exact:true}),b=card.getByRole('button',{name:'B. B option',exact:true}),c=card.getByRole('button',{name:'C. C option',exact:true});
 await c.click();await a.click();
 let responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/admin/attempts/review')&&r.request().method()==='POST');
 await card.getByRole('button',{name:'提交作答',exact:true}).click();let response=await responsePromise;let answer=await response.json();
 await card.getByText(/判定：作答正确/).waitFor();
 console.log('MULTI_BASIC',JSON.stringify({submitted:answer.attempt.submitted_answer,verdict:answer.evaluation.verdict}));
 // Hold an actual backend response, alter panel generation, then deliver the old response.
 await c.click(); // A only, invalidates prior evaluation.
 let release, heldResolve;const held=new Promise(r=>heldResolve=r),gate=new Promise(r=>release=r);let old;
 await page.route('**/api/admin/attempts/review',async route=>{const r=await route.fetch();old=await r.json();heldResolve();await gate;await route.fulfill({response:r});});
 await card.getByRole('button',{name:'提交作答',exact:true}).click();await held;
 await card.getByRole('button',{name:'收起',exact:true}).click();await card.getByRole('button',{name:'再答',exact:true}).click();await b.click();release();
 await card.getByText(/判定：作答有误/).waitFor();
 console.log('RACE_VISIBLE',JSON.stringify({oldSubmitted:old.attempt.submitted_answer,newBPressed:await b.getAttribute('aria-pressed'),oldVerdictVisible:true,oldAttempt:old.attempt.id}));
 await page.screenshot({path:path.join(__dirname,'race-stale-evaluation.png'),fullPage:true});
 const submitPromise=page.waitForResponse(r=>/\/api\/admin\/review\/items\/.+\/submit$/.test(r.url()));
 await card.getByRole('button',{name:/提交 0 分复习结果/}).click();const submitted=await submitPromise;
 const records=await call(`/api/admin/review/items/${fixture.review_item_id}/records`);const newest=JSON.parse(records.body)[0];
 console.log('RACE_PERSISTED',JSON.stringify({submitStatus:submitted.status(),recordAttempt:newest.attempt_id,oldAttempt:old.attempt.id,boundOldAttempt:newest.attempt_id===old.attempt.id,rating:newest.rating}));
 console.log('KP_READBACK',JSON.stringify(await call('/api/admin/knowledge-points/analytics')));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
