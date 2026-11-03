/* Rook Rally: a paddle game between solves.
   White rook (you) against Black rook (the computer); the ball is a pawn.
   Eight returns in one rally promote the pawn to a queen: faster, and the point counts double.
   First to 7 points takes the match, printed the way a game result is: 1-0 or 0-1. */
(function(){
  const canvas=document.getElementById('rally');
  if(!canvas) return;
  const ctx=canvas.getContext('2d');
  const statusEl=document.getElementById('rallyStatus');
  const playBtn=document.getElementById('rallyPlay');

  // Logical field: 16 x 9 squares of 40 units; drawn scaled to the canvas width.
  const SQ=40, W=16*SQ, H=9*SQ;
  const PAD_W=12, PAD_H=72, PAD_X=26;
  const BALL_R=11;
  const TARGET=7, PROMOTE_AT=8;
  const BASE_SPEED=330, MAX_SPEED=820, SPEEDUP=1.045, QUEEN_BOOST=1.2;
  const KEY_SPEED=480, AI_SPEED=280;
  const GLYPH_FONT="'DejaVu Sans','Segoe UI Symbol','Apple Symbols',serif";

  let scale=1, colours={}, hatch=null;
  let state='idle';          // idle | serve | play | point | paused | over
  let you={y:H/2, score:0}, cpu={y:H/2, score:0, aim:0};
  let ball={x:W/2, y:H/2, vx:0, vy:0, speed:BASE_SPEED, queen:false};
  let returns=0, serveDir=1, timer=0, lastMsg='', pointerY=null;
  const keys={up:false, down:false};

  function readColours(){
    const cs=getComputedStyle(document.documentElement);
    const v=n=>cs.getPropertyValue(n).trim();
    colours={paper:v('--paper')||'#fff', ink:v('--ink')||'#000', grey:v('--grey')||'#767472',
             hatch:v('--hatch')||'#b9b7b4', award:v('--award')||'#a51c16', tint:v('--tint')||'#f2f1ee'};
  }
  function makeHatch(){
    const c=document.createElement('canvas'), n=8; c.width=c.height=n;
    const g=c.getContext('2d');
    g.fillStyle=colours.paper; g.fillRect(0,0,n,n);
    g.strokeStyle=colours.hatch; g.lineWidth=1.1;
    g.beginPath(); g.moveTo(0,n); g.lineTo(n,0); g.moveTo(-n/2,n/2); g.lineTo(n/2,-n/2);
    g.moveTo(n/2,n*1.5); g.lineTo(n*1.5,n/2); g.stroke();
    hatch=ctx.createPattern(c,'repeat');
  }
  function resize(){
    const cssW=canvas.clientWidth||W, dpr=window.devicePixelRatio||1;
    canvas.style.height=(cssW*H/W)+'px';
    canvas.width=Math.round(cssW*dpr); canvas.height=Math.round(cssW*H/W*dpr);
    scale=canvas.width/W;
    readColours(); makeHatch(); draw();
  }

  function say(msg){ if(msg!==lastMsg){ statusEl.textContent=msg; lastMsg=msg; } }
  function clamp(v,a,b){ return Math.max(a,Math.min(b,v)); }

  function resetBall(dir){
    ball={x:W/2, y:H/2, vx:0, vy:0, speed:BASE_SPEED, queen:false};
    returns=0; serveDir=dir; state='serve'; timer=0.7;
  }
  function launch(){
    const ang=(Math.random()*0.7-0.35);
    ball.vx=Math.cos(ang)*ball.speed*serveDir;
    ball.vy=Math.sin(ang)*ball.speed;
    cpu.aim=(Math.random()*2-1)*14;
    state='play';
  }
  function newMatch(){
    you.score=0; cpu.score=0; you.y=cpu.y=H/2;
    resetBall(Math.random()<0.5?1:-1);
    say('Rally on. Move your rook with the mouse, a finger, W/S or the arrow keys. Space pauses.');
    canvas.focus({preventScroll:true});
  }

  function hitPaddle(py, side){
    const off=clamp((ball.y-py)/(PAD_H/2),-1,1);
    const ang=off*Math.PI/3.2;
    returns++;
    ball.speed=Math.min(MAX_SPEED, ball.speed*SPEEDUP);
    if(!ball.queen && returns>=PROMOTE_AT){
      ball.queen=true; ball.speed=Math.min(MAX_SPEED*QUEEN_BOOST, ball.speed*QUEEN_BOOST);
      say('Promotion! The pawn is a queen: faster, and this point counts double.');
    }
    ball.vx=Math.cos(ang)*ball.speed*side;
    ball.vy=Math.sin(ang)*ball.speed;
    // the Black rook misjudges more as the rally gets longer and faster
    if(side>0) cpu.aim=(Math.random()*2-1)*(12+returns*3.2+(ball.queen?8:0));
  }

  function score(winner){
    const pts=ball.queen?2:1;
    if(winner==='you'){ you.score+=pts; } else { cpu.score+=pts; }
    const who=winner==='you'?'White':'Black';
    if(you.score>=TARGET||cpu.score>=TARGET){
      state='over';
      const res=you.score>cpu.score?'1–0':'0–1';
      say(`${res}. ${you.score>cpu.score?'White wins the match':'Black wins the match'} ${you.score}:${cpu.score}. Press Play for a new match.`);
      playBtn.textContent='New match';
      return;
    }
    say(`${who} scores${pts===2?' 2 (queen)':''}. ${you.score}:${cpu.score}`);
    state='point'; timer=0.9;
    serveDir = winner==='you' ? 1 : -1;   // the conceding side receives
  }

  // Where will the ball cross x, bouncing off the top and bottom edges?
  function predictY(x){
    if(ball.vx<=0) return H/2;
    const t=(x-ball.x)/ball.vx;
    let y=ball.y+ball.vy*t;
    const lo=BALL_R, hi=H-BALL_R, span=hi-lo;
    y-=lo; const period=2*span;
    y=((y%period)+period)%period;
    if(y>span) y=period-y;
    return y+lo;
  }

  function step(dt){
    // White rook: pointer target or keys
    if(pointerY!==null){ you.y += clamp(pointerY-you.y, -1400*dt, 1400*dt); }
    if(keys.up) you.y-=KEY_SPEED*dt;
    if(keys.down) you.y+=KEY_SPEED*dt;
    you.y=clamp(you.y,PAD_H/2,H-PAD_H/2);

    // Black rook: follows the predicted crossing once the ball heads its way, else drifts home
    const cpuX=W-PAD_X;
    let goal=H/2;
    if(state==='play' && ball.vx>0 && ball.x>W*0.4) goal=predictY(cpuX-PAD_W/2-BALL_R)+cpu.aim;
    const sp=AI_SPEED*(1+Math.min(returns,8)*0.02);
    cpu.y+=clamp(goal-cpu.y,-sp*dt,sp*dt);
    cpu.y=clamp(cpu.y,PAD_H/2,H-PAD_H/2);

    if(state==='serve'||state==='point'){
      timer-=dt;
      if(timer<=0){ if(state==='point') resetBall(serveDir); else launch(); }
      return;
    }
    if(state!=='play') return;

    ball.x+=ball.vx*dt; ball.y+=ball.vy*dt;
    if(ball.y<BALL_R){ ball.y=BALL_R; ball.vy=Math.abs(ball.vy); }
    if(ball.y>H-BALL_R){ ball.y=H-BALL_R; ball.vy=-Math.abs(ball.vy); }

    const youFace=PAD_X+PAD_W/2, cpuFace=cpuX-PAD_W/2;
    if(ball.vx<0 && ball.x-BALL_R<=youFace && ball.x-BALL_R>=youFace-PAD_W-12 &&
       Math.abs(ball.y-you.y)<=PAD_H/2+BALL_R){
      ball.x=youFace+BALL_R; hitPaddle(you.y,1);
    }
    if(ball.vx>0 && ball.x+BALL_R>=cpuFace && ball.x+BALL_R<=cpuFace+PAD_W+12 &&
       Math.abs(ball.y-cpu.y)<=PAD_H/2+BALL_R){
      ball.x=cpuFace-BALL_R; hitPaddle(cpu.y,-1);
    }
    if(ball.x<-BALL_R*2) score('cpu');
    else if(ball.x>W+BALL_R*2) score('you');
  }

  function glyph(ch,x,y,size,fill){
    ctx.font=`${size}px ${GLYPH_FONT}`; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillStyle=fill; ctx.fillText(ch,x,y);
  }
  function draw(){
    ctx.setTransform(scale,0,0,scale,0,0);
    ctx.fillStyle=colours.paper; ctx.fillRect(0,0,W,H);
    for(let r=0;r<9;r++) for(let f=0;f<16;f++) if((r+f)%2){ ctx.fillStyle=hatch||colours.tint; ctx.fillRect(f*SQ,r*SQ,SQ,SQ); }
    // the middle file boundary, as a plain rule
    ctx.strokeStyle=colours.hatch; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(W/2,0); ctx.lineTo(W/2,H); ctx.stroke();
    ctx.strokeStyle=colours.ink; ctx.lineWidth=2; ctx.strokeRect(1,1,W-2,H-2);

    // score, printed like a match card
    ctx.font=`600 26px "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif`;
    ctx.textAlign='center'; ctx.textBaseline='top';
    ctx.fillStyle=colours.paper; ctx.fillRect(W/2-58,8,116,34);
    ctx.strokeStyle=colours.ink; ctx.lineWidth=1; ctx.strokeRect(W/2-58,8,116,34);
    ctx.fillStyle=colours.ink; ctx.fillText(`${you.score} : ${cpu.score}`,W/2,12);

    // rooks
    const drawRook=(x,y,white)=>{
      ctx.fillStyle=white?colours.paper:colours.ink; ctx.strokeStyle=colours.ink; ctx.lineWidth=2;
      ctx.fillRect(x-PAD_W/2,y-PAD_H/2,PAD_W,PAD_H); ctx.strokeRect(x-PAD_W/2,y-PAD_H/2,PAD_W,PAD_H);
    };
    drawRook(PAD_X,you.y,true); drawRook(W-PAD_X,cpu.y,false);
    glyph('♖',PAD_X+30,22,26,colours.grey);
    glyph('♜',W-PAD_X-30,22,26,colours.grey);

    // the pawn (or queen)
    if(state!=='over'){
      ctx.fillStyle=colours.paper; ctx.strokeStyle=ball.queen?colours.award:colours.ink; ctx.lineWidth=2;
      ctx.beginPath(); ctx.arc(ball.x,ball.y,BALL_R+2,0,Math.PI*2); ctx.fill(); ctx.stroke();
      glyph(ball.queen?'♛':'♟',ball.x,ball.y+1,19,ball.queen?colours.award:colours.ink);
    }

    // overlays
    const banner=(t1,t2)=>{
      ctx.fillStyle=colours.paper; ctx.globalAlpha=0.92; ctx.fillRect(W/2-190,H/2-46,380,92); ctx.globalAlpha=1;
      ctx.strokeStyle=colours.ink; ctx.lineWidth=1.5; ctx.strokeRect(W/2-190,H/2-46,380,92);
      ctx.fillStyle=colours.ink; ctx.textAlign='center'; ctx.textBaseline='middle';
      ctx.font=`600 24px "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif`; ctx.fillText(t1,W/2,H/2-14);
      ctx.fillStyle=colours.grey; ctx.font=`16px "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif`;
      ctx.fillText(t2,W/2,H/2+18);
    };
    if(state==='idle') banner('Rook Rally','Click here or press Play to start');
    else if(state==='paused') banner('Paused','Click or press Space to go on');
    else if(state==='over'){
      const youWon=you.score>cpu.score;
      banner(youWon?'1–0  White wins':'0–1  Black wins', `${you.score} : ${cpu.score}. Press Play for a new match`);
    }
  }

  let last=0, raf=0;
  function frame(t){
    const dt=Math.min(0.033,(t-(last||t))/1000); last=t;
    step(dt); draw();
    raf = (state==='idle'||state==='paused'||state==='over') ? 0 : requestAnimationFrame(frame);
    // a finger drag steers the rook only while a rally runs; otherwise the page scrolls as usual
    const ta = raf ? 'none' : 'auto';
    if(canvas.style.touchAction!==ta){ canvas.style.touchAction=ta; canvas.style.cursor = raf ? 'none' : 'pointer'; }
  }
  function run(){ if(!raf){ last=0; raf=requestAnimationFrame(frame); } }

  function pause(){
    if(state==='play'||state==='serve'||state==='point'){ state='paused'; say('Paused.'); playBtn.textContent='Resume'; draw(); }
  }
  function resume(){
    if(state==='paused'){ state=(ball.vx||ball.vy)?'play':'serve'; if(state==='serve') timer=0.5;
      playBtn.textContent='Pause'; say(`${you.score}:${cpu.score}`); canvas.focus({preventScroll:true}); run(); }
  }
  function toggle(){
    if(state==='idle'||state==='over'){ newMatch(); playBtn.textContent='Pause'; run(); }
    else if(state==='paused') resume();
    else pause();
  }

  playBtn.addEventListener('click',toggle);
  canvas.addEventListener('click',()=>{ if(state==='idle'||state==='over'||state==='paused') toggle(); });
  canvas.addEventListener('keydown',e=>{
    if(e.key==='ArrowUp'||e.key==='w'||e.key==='W'){ keys.up=true; pointerY=null; e.preventDefault(); }
    else if(e.key==='ArrowDown'||e.key==='s'||e.key==='S'){ keys.down=true; pointerY=null; e.preventDefault(); }
    else if(e.key===' '||e.key==='Enter'){ toggle(); e.preventDefault(); }
  });
  canvas.addEventListener('keyup',e=>{
    if(e.key==='ArrowUp'||e.key==='w'||e.key==='W') keys.up=false;
    if(e.key==='ArrowDown'||e.key==='s'||e.key==='S') keys.down=false;
  });
  canvas.addEventListener('blur',()=>{ keys.up=keys.down=false; });
  canvas.addEventListener('pointermove',e=>{
    const r=canvas.getBoundingClientRect();
    pointerY=(e.clientY-r.top)/r.height*H;
  });
  canvas.addEventListener('pointerdown',e=>{
    const r=canvas.getBoundingClientRect();
    pointerY=(e.clientY-r.top)/r.height*H;
  });
  document.addEventListener('visibilitychange',()=>{ if(document.hidden) pause(); });
  if('IntersectionObserver' in window){
    new IntersectionObserver(es=>{ for(const e of es) if(!e.isIntersecting) pause(); },{threshold:0.25}).observe(canvas);
  }
  window.addEventListener('resize',resize);

  resize();
  say('Rook Rally: your White rook on the left against the Black rook. First to 7 wins.');
})();
