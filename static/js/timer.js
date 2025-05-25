// Em static/js/timer.js

// Para o título do documento: Pegue a data exibida no H1 do dashboard
let dataExibicaoParaTitulo = "Dia"; // Valor padrão
document.addEventListener('DOMContentLoaded', () => {
    const tituloH1Dashboard = document.querySelector('.page-title-header-v6');
    if (tituloH1Dashboard) { // Verifica se o elemento existe
        const h1Texto = tituloH1Dashboard.textContent || "";
        if (h1Texto.includes(' - ')) {
            dataExibicaoParaTitulo = h1Texto.split(' - ')[1].trim();
        } else if (h1Texto.toLowerCase().startsWith('dashboard')) {
            // Caso não tenha data específica, mas seja o dashboard de hoje
            dataExibicaoParaTitulo = "Hoje";
        }
    }
    // Inicializa o app do timer
    initializeTimerApp();
});


function initializeTimerApp() {
    let timerInterval;
    let timeLeftInSeconds;
    let currentMode = 'pomodoro'; // 'timer' ou 'pomodoro'
    let timerState = 'stopped'; // 'stopped', 'running', 'paused'

    // Configurações Pomodoro
    let pomodoroCurrentPhase = 'work'; // 'work', 'shortBreak', 'longBreak'
    const pomodoroDurations = { // em segundos
        work: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    };
    let pomodorosCompletedCycle = 0;
    const pomodorosPerLongBreak = 4;

    // Elementos DOM
    const timeDisplayElement = document.getElementById('time-display');
    const statusDisplayElement = document.getElementById('timer-status-display');

    const btnModeTimer = document.getElementById('btn-mode-timer');
    const btnModePomodoro = document.getElementById('btn-mode-pomodoro');

    const standardTimerControlsUI = document.getElementById('standard-timer-controls');
    const timerMinutesInputElement = document.getElementById('timer-minutes-input');
    const btnTimerStart = document.getElementById('btn-timer-start');
    const btnTimerPause = document.getElementById('btn-timer-pause');
    const btnTimerReset = document.getElementById('btn-timer-reset');

    const pomodoroControlsUI = document.getElementById('pomodoro-controls');
    const btnPomodoroStart = document.getElementById('btn-pomodoro-start');
    const btnPomodoroPause = document.getElementById('btn-pomodoro-pause');
    const btnPomodoroSkip = document.getElementById('btn-pomodoro-skip');
    const btnPomodoroReset = document.getElementById('btn-pomodoro-reset');

    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    function updateTimerDisplay() {
        timeDisplayElement.textContent = formatTime(timeLeftInSeconds);
        if (timerState === 'running') {
            let titlePhase = "";
            if (currentMode === 'pomodoro') {
                if (pomodoroCurrentPhase === 'work') titlePhase = "Foco";
                else if (pomodoroCurrentPhase === 'shortBreak') titlePhase = "Pausa Curta";
                else titlePhase = "Pausa Longa";
            } else {
                titlePhase = "Timer";
            }
            document.title = `${formatTime(timeLeftInSeconds)} - ${titlePhase} | Focus Lab`;
        } else {
             document.title = `Dashboard - ${dataExibicaoParaTitulo} | Focus Lab`;
        }
    }
    
    function updateStatusDisplay() {
        if (currentMode === 'timer') {
            statusDisplayElement.textContent = `Timer ${timerState === 'paused' ? 'Pausado' : ''}`;
             if (timerState === 'stopped' && timeLeftInSeconds === 0 && !(parseInt(timerMinutesInputElement.value, 10) * 60 === 0)) {
                statusDisplayElement.textContent = "Timer Concluído!";
            }
        } else { // pomodoro
            let phaseText = "";
            if (pomodoroCurrentPhase === 'work') phaseText = "Foco";
            else if (pomodoroCurrentPhase === 'shortBreak') phaseText = "Pausa Curta";
            else phaseText = "Pausa Longa";
            statusDisplayElement.textContent = `Pomodoro: ${phaseText} ${timerState === 'paused' ? '(Pausado)' : ''}`;
        }
    }

    function stopInterval() {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    function updateButtonStates() {
        if (currentMode === 'timer') {
            // Botão Iniciar/Continuar: Visível se parado ou pausado.
            btnTimerStart.style.display = (timerState === 'running') ? 'none' : 'inline-block';
            btnTimerStart.textContent = (timerState === 'paused') ? 'Continuar' : 'Iniciar';

            // Botão Pausar: Visível apenas se rodando.
            btnTimerPause.style.display = (timerState === 'running') ? 'inline-block' : 'none';

            // Botão Resetar: Desabilitado se parado E no valor inicial do input.
            const currentInputValueSeconds = parseInt(timerMinutesInputElement.value, 10) * 60;
            btnTimerReset.disabled = (timerState === 'stopped' && timeLeftInSeconds === currentInputValueSeconds);

        } else { // pomodoro
            // Botão Iniciar Foco/Pausa/Continuar: Visível se parado ou pausado.
            btnPomodoroStart.style.display = (timerState === 'running') ? 'none' : 'inline-block';
            if (timerState === 'paused') {
                btnPomodoroStart.textContent = 'Continuar';
            } else { // stopped or other
                btnPomodoroStart.textContent = (pomodoroCurrentPhase === 'work' ? 'Iniciar Foco' : (pomodoroCurrentPhase === 'shortBreak' ? 'Iniciar Pausa Curta' : 'Iniciar Pausa Longa'));
            }
            
            // Botão Pausar: Visível apenas se rodando.
            btnPomodoroPause.style.display = (timerState === 'running') ? 'inline-block' : 'none';
            
            // Botão Pular: Visível se rodando ou pausado.
            btnPomodoroSkip.style.display = (timerState !== 'stopped') ? 'inline-block' : 'none';
            
            // Botão Resetar Ciclos: Desabilitado se parado E na primeira fase de trabalho E tempo inicial.
            btnPomodoroReset.disabled = (timerState === 'stopped' && pomodoroCurrentPhase === 'work' && pomodorosCompletedCycle === 0 && timeLeftInSeconds === pomodoroDurations.work);
        }
    }


    function timerEnds() {
        stopInterval();
        timerState = 'stopped';
        
        document.title = "Tempo Esgotado! | Focus Lab";
        // alert("Tempo Esgotado!"); 

        if (currentMode === 'pomodoro') {
            transitionPomodoroPhase();
        } else {
            // btnTimerStart.textContent = 'Iniciar'; // updateButtonStates fará isso
            // btnTimerStart.style.display = 'inline-block';
            // btnTimerPause.style.display = 'none';
            statusDisplayElement.textContent = "Timer Concluído!"; // Mensagem específica
            updateButtonStates(); // Garante que os botões voltem ao estado inicial do Timer
        }
    }

    function startCountdown() {
        // Se estiver parado e for o modo timer, pega o valor do input
        if (timerState === 'stopped' && currentMode === 'timer') {
            const newTime = parseInt(timerMinutesInputElement.value, 10) * 60;
            if (isNaN(newTime) || newTime <= 0) {
                alert("Por favor, insira uma duração válida para o timer.");
                timerMinutesInputElement.value = Math.floor(pomodoroDurations.work / 60); // Reset input to default
                return;
            }
            timeLeftInSeconds = newTime;
        }
        // Se estiver parado e for pomodoro, e o tempo for zero (após um ciclo), reseta para a fase atual
        if (timerState === 'stopped' && currentMode === 'pomodoro' && timeLeftInSeconds === 0) {
             timeLeftInSeconds = pomodoroDurations[pomodoroCurrentPhase];
        }


        timerState = 'running';
        updateButtonStates();
        updateStatusDisplay();
        updateTimerDisplay(); // Para mostrar o tempo correto antes do primeiro intervalo

        stopInterval(); 
        timerInterval = setInterval(() => {
            if (timeLeftInSeconds > 0) {
                timeLeftInSeconds--;
                updateTimerDisplay();
            } else {
                timerEnds();
            }
        }, 1000);
    }

    function pauseCountdown() {
        stopInterval();
        timerState = 'paused';
        updateButtonStates();
        updateStatusDisplay();
        document.title = `Pausado: ${formatTime(timeLeftInSeconds)} | Focus Lab`;
    }

    function resetTimerValues() {
        stopInterval();
        timerState = 'stopped';
        if (currentMode === 'timer') {
            timeLeftInSeconds = parseInt(timerMinutesInputElement.value, 10) * 60 || (25 * 60);
        } else { // pomodoro
            pomodorosCompletedCycle = 0;
            pomodoroCurrentPhase = 'work';
            timeLeftInSeconds = pomodoroDurations.work;
        }
        updateTimerDisplay();
        updateButtonStates();
        updateStatusDisplay();
        document.title = `Dashboard - ${dataExibicaoParaTitulo} | Focus Lab`;
    }
    
    function switchToMode(mode) {
        currentMode = mode;
        resetTimerValues(); 

        if (mode === 'timer') {
            standardTimerControlsUI.style.display = 'flex';
            pomodoroControlsUI.style.display = 'none';
            btnModeTimer.classList.add('active');
            btnModePomodoro.classList.remove('active');
        } else { // pomodoro
            standardTimerControlsUI.style.display = 'none';
            pomodoroControlsUI.style.display = 'flex';
            btnModePomodoro.classList.add('active');
            btnModeTimer.classList.remove('active');
        }
        // updateStatusDisplay(); // resetTimerValues já chama updateStatusDisplay
    }

    function transitionPomodoroPhase() {
        if (pomodoroCurrentPhase === 'work') {
            pomodorosCompletedCycle++;
            if (pomodorosCompletedCycle > 0 && pomodorosCompletedCycle % pomodorosPerLongBreak === 0) {
                pomodoroCurrentPhase = 'longBreak';
                timeLeftInSeconds = pomodoroDurations.longBreak;
            } else {
                pomodoroCurrentPhase = 'shortBreak';
                timeLeftInSeconds = pomodoroDurations.shortBreak;
            }
        } else { 
            pomodoroCurrentPhase = 'work';
            timeLeftInSeconds = pomodoroDurations.work;
        }
        // updateTimerDisplay(); // Será chamado por startCountdown
        // updateButtonStates(); // Será chamado por startCountdown
        updateStatusDisplay(); // Atualiza o status antes de iniciar
        startCountdown(); 
    }
    
    function skipCurrentPomodoroPhase() {
        stopInterval(); 
        timeLeftInSeconds = 0; // Força o fim da fase atual
        timerEnds();    
    }

    // Event Listeners
    btnModeTimer.addEventListener('click', () => switchToMode('timer'));
    btnModePomodoro.addEventListener('click', () => switchToMode('pomodoro'));

    timerMinutesInputElement.addEventListener('change', () => {
        if (currentMode === 'timer' && timerState === 'stopped') {
            const newTime = parseInt(timerMinutesInputElement.value, 10) * 60;
            if (newTime > 0) {
                timeLeftInSeconds = newTime;
                updateTimerDisplay();
                updateButtonStates(); // Atualiza estado do botão reset
            } else {
                timerMinutesInputElement.value = Math.floor((timeLeftInSeconds || pomodoroDurations.work) / 60) ; 
            }
        }
    });

    btnTimerStart.addEventListener('click', startCountdown);
    btnTimerPause.addEventListener('click', pauseCountdown);
    btnTimerReset.addEventListener('click', resetTimerValues);

    btnPomodoroStart.addEventListener('click', startCountdown);
    btnPomodoroPause.addEventListener('click', pauseCountdown);
    btnPomodoroSkip.addEventListener('click', skipCurrentPomodoroPhase);
    btnPomodoroReset.addEventListener('click', resetTimerValues);
    
    // Inicialização
    switchToMode('pomodoro'); 
}