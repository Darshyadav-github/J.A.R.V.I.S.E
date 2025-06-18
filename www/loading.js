(function(){
    const screens = Array.from(document.querySelectorAll('.screen'));
    let current = 0;
    const timers = [];

    function setT(fn, t){ const id = setTimeout(fn, t); timers.push(id); return id; }
    function clearAll(){ timers.forEach(clearTimeout); }

    function goto(idx){
        screens[idx].classList.add('active');
        setTimeout(()=>screens[current].classList.remove('active'),600);
        current = idx;
    }

    function next(idx, cb){
        goto(idx);
        if(cb) setT(cb,1200);
    }

    function startSequence(){
        screens[0].classList.add('active');
        setT(()=>next(1, ()=>next(2, startModules)),1200);
    }

    function startModules(){
        const modules = document.querySelectorAll('.module');
        const log = document.getElementById('log');
        const countdown = document.getElementById('countdown');
        const beep = document.getElementById('beep');
        let mIndex = 0;

        function logMsg(name){
            const now = new Date().toTimeString().split(' ')[0];
            log.innerHTML += `[${now}] ${name}... [OK]<br>`;
            log.scrollTop = log.scrollHeight;
        }

        function runModule(mod){
            const prog = mod.querySelector('.progress');
            const percent = mod.querySelector('.percent');
            let val = 0;
            const step = setInterval(()=>{
                val += 20;
                if(val>100) val=100;
                percent.textContent = val+'%';
                prog.style.strokeDashoffset = 339 - 339*(val/100);
                if(val===100){
                    clearInterval(step);
                    mod.classList.add('ready');
                    logMsg(mod.dataset.name);
                    mIndex++;
                    if(mIndex<modules.length) runModule(modules[mIndex]);
                    else startCountdown();
                }
            },100);
        }

        function startCountdown(){
            let c = 3;
            countdown.textContent = `LAUNCH IN T-0${c}s`;
            countdown.style.opacity = 1;
            const cd = setInterval(()=>{
                beep && beep.play();
                c--;
                if(c>=0){
                    countdown.textContent = `LAUNCH IN T-0${c}s`;
                }else{
                    clearInterval(cd);
                    next(3, ()=>next(4, ()=>next(5, clearAll)));
                }
            },1000);
        }

        runModule(modules[0]);
    }

    window.addEventListener('load', startSequence);
})();
