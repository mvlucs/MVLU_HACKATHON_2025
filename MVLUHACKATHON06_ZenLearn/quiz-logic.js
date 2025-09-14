// quiz-logic.js
// Behavior:
// - 25 minute timer starts when user clicks Start
// - Each (subject,set) has 3 attempts stored in localStorage under key "attempts_<subject>_<set>"
// - Attempt is consumed when user STARTS a quiz (so Quit or Submit both consume that attempt)
// - Start button disabled after 3 attempts used
// - Quit shows confirm; if confirmed, returns to index.html

let timer = null;
let timeLeft = 25 * 60; // seconds
let currentQuestions = [];
let currentSubject = null;
let currentSet = null;
const MAX_ATTEMPTS = 3;

function keyFor(subject, set) {
  return `attempts_${subject}_${set}`;
}

function getAttemptsUsed(subject, set) {
  const k = keyFor(subject, set);
  const v = localStorage.getItem(k);
  return v ? parseInt(v, 10) : 0;
}

function setAttemptsUsed(subject, set, n) {
  const k = keyFor(subject, set);
  localStorage.setItem(k, String(n));
}

// update the attempts info UI and Start button state
function updateAttemptsInfoUI() {
  const subject = document.getElementById('subject')?.value;
  const set = document.getElementById('setNum')?.value;
  const infoEl = document.getElementById('attemptsInfo');
  const startBtn = document.getElementById('startBtn') || document.querySelector('.btn-primary');

  if (!subject || !set || !infoEl) return;

  const used = getAttemptsUsed(subject, set);
  const left = Math.max(0, MAX_ATTEMPTS - used);

  infoEl.textContent = `Attempts left: ${left} / ${MAX_ATTEMPTS}`;

  if (left <= 0) {
    if (startBtn) {
      startBtn.disabled = true;
      startBtn.style.opacity = '0.6';
      startBtn.title = 'No attempts left for this set.';
    }
  } else {
    if (startBtn) {
      startBtn.disabled = false;
      startBtn.style.opacity = '';
      startBtn.title = '';
    }
  }
}

// Wire change events so the attempts info updates when user changes subject/set
document.addEventListener('DOMContentLoaded', () => {
  const subj = document.getElementById('subject');
  const set = document.getElementById('setNum');
  const startBtn = document.getElementById('startBtn');

  if (subj) subj.addEventListener('change', updateAttemptsInfoUI);
  if (set) set.addEventListener('change', updateAttemptsInfoUI);

  // handle Start button by id if present
  if (startBtn) {
    startBtn.addEventListener('click', (e) => {
      e.preventDefault();
      startQuiz();
    });
  } else {
    // fallback: find first primary button
    const fallback = document.querySelector('.btn-primary');
    if (fallback) fallback.addEventListener('click', (e)=>{ e.preventDefault(); startQuiz(); });
  }

  // hookup submit and quit if not already bound
  const sub = document.getElementById('submitBtn');
  if (sub) sub.addEventListener('click', (e)=>{ e.preventDefault(); submitQuiz(); });

  const quit = document.getElementById('quitBtn');
  if (quit) quit.addEventListener('click', (e)=>{ e.preventDefault(); quitQuiz(); });

  // initial attempts UI
  updateAttemptsInfoUI();
});

// Start quiz: checks attempts, increments used, renders questions and starts timer
function startQuiz() {
  currentSubject = document.getElementById('subject')?.value;
  currentSet = document.getElementById('setNum')?.value;

  if (!currentSubject || !currentSet) {
    alert('Please select a subject and set.');
    return;
  }

  // check quiz existence
  if (!window.quizData || !quizData[currentSubject] || !quizData[currentSubject][currentSet]) {
    alert('Selected set not available. Contact admin or try another set.');
    return;
  }

  // check attempts left
  const used = getAttemptsUsed(currentSubject, currentSet);
  if (used >= MAX_ATTEMPTS) {
    alert(`You have used all ${MAX_ATTEMPTS} attempts for this set.`);
    updateAttemptsInfoUI();
    return;
  }

  // increment attempt (consume attempt immediately on start)
  setAttemptsUsed(currentSubject, currentSet, used + 1);
  updateAttemptsInfoUI();

  // load questions (10 questions expected)
  currentQuestions = quizData[currentSubject][currentSet];

  // render UI
  document.getElementById('quizTitle').innerText = `${currentSubject.toUpperCase()} — Set ${currentSet}`;
  const form = document.getElementById('quizForm');
  form.innerHTML = '';

  currentQuestions.forEach((q, i) => {
    const wrap = document.createElement('div');
    wrap.className = 'question';
    const qHtml = `<h4>${i+1}. ${q.q}</h4>`;
    const optsHtml = q.options.map(o =>
      `<label class="option"><input type="radio" name="q${i}" value="${escapeHtml(o)}"> ${escapeHtml(o)}</label>`
    ).join('');
    wrap.innerHTML = qHtml + optsHtml;
    form.appendChild(wrap);
  });

  // show quiz box
  document.getElementById('quizBox').classList.remove('hidden');

  // set timer (25 minutes)
  timeLeft = 25 * 60;
  updateTimerDisplay();
  clearInterval(timer);
  timer = setInterval(() => {
    timeLeft--;
    updateTimerDisplay();
    if (timeLeft <= 0) {
      // time up -> auto submit
      clearInterval(timer);
      window.onbeforeunload = null;
      alert('Time is up — your answers will be submitted automatically.');
      finalizeSubmit();
    }
  }, 1000);

  // prevent accidental navigation
  window.onbeforeunload = function() {
    return 'You have an ongoing quiz. Leaving will forfeit the attempt.';
  };
}

// helper: safe text
function escapeHtml(s) {
  if (typeof s !== 'string') return s;
  return s.replace(/[&<>"']/g, function (m) {
    return ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[m];
  });
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  if (!timerEl) return;
  const m = Math.floor(Math.max(0, timeLeft) / 60).toString().padStart(2, '0');
  const s = (timeLeft % 60).toString().padStart(2, '0');
  timerEl.innerText = `${m}:${s}`;
}

// Called when user presses Submit
function submitQuiz() {
  // double-check if a quiz is actually running
  if (!currentQuestions || currentQuestions.length === 0) {
    alert('No quiz is running.');
    return;
  }
  // ask confirm before submit? (optional) - we'll submit directly
  finalizeSubmit();
}

function finalizeSubmit() {
  clearInterval(timer);
  window.onbeforeunload = null;

  let score = 0;
  currentQuestions.forEach((q, i) => {
    const sel = document.querySelector(`input[name="q${i}"]:checked`);
    if (sel && sel.value === q.ans) score++;
  });

  // store results
  localStorage.setItem('lastScore', String(score));
  localStorage.setItem('lastSubject', currentSubject);
  localStorage.setItem('lastSet', currentSet);
  localStorage.setItem('lastTimeTaken', String(25 * 60 - timeLeft));
  alert(`✅ Your Score: ${score} / ${currentQuestions.length}`);

  // open feedback modal
  const fb = document.getElementById('feedbackModal');
  if (fb) fb.style.display = 'flex';

  // reset currentQuestions so user cannot re-submit same render
  currentQuestions = [];
}

// Quit quiz - confirm and then exit to index (attempt already consumed)
function quitQuiz() {
  if (!currentQuestions || currentQuestions.length === 0) {
    // nothing running - simply go back
    window.location.href = 'index.html';
    return;
  }
  const ok = confirm('Do you really want to quit? Your current attempt will be lost.');
  if (ok) {
    clearInterval(timer);
    window.onbeforeunload = null;
    // note: attempt already incremented on start, so no extra change needed
    // go back
    window.location.href = 'index.html';
  }
}

// Save feedback (simple numeric rating) and go home
function saveFeedback() {
  const fbVal = document.getElementById('feedback')?.value || '';
  const key = `feedback_${currentSubject}_${currentSet}_${Date.now()}`;
  if (fbVal) localStorage.setItem(key, String(fbVal));
  alert('Thanks for your feedback!');
  // hide modal and go to home
  const fb = document.getElementById('feedbackModal');
  if (fb) fb.style.display = 'none';
  // update attempts UI (in case user returns to same set)
  updateAttemptsInfoUI();
  window.location.href = 'index.html';
}

function closeFeedback(){
  const fb = document.getElementById('feedbackModal');
  if (fb) fb.style.display = 'none';
  updateAttemptsInfoUI();
}
