// Load stats from localStorage
let learners = localStorage.getItem("learners") || 0;
let quizzes = localStorage.getItem("quizzes") || 0;
let satisfaction = localStorage.getItem("satisfaction") || 0;

// Show stats on page load
document.getElementById("learners").innerText = learners;
document.getElementById("quizzes").innerText = quizzes;
document.getElementById("satisfaction").innerText = satisfaction + "%";

// Signup function
function signup() {
  learners++;
  satisfaction = Math.min(100, parseInt(satisfaction) + 1);

  localStorage.setItem("learners", learners);
  localStorage.setItem("satisfaction", satisfaction);

  document.getElementById("learners").innerText = learners;
  document.getElementById("satisfaction").innerText = satisfaction + "%";

  openPopup("profile");
}

// Popup handling
function openPopup(type) {
  let title = "", text = "";

  switch(type) {
    case "about":
      title = "About ZenLearn";
      text = "ZenLearn is a mindful learning platform designed to make studying less stressful and more effective. It combines quizzes, daily tracking, curated topics, and the Pomodoro study style to help learners stay focused and balanced.";
      break;

    case "quiz": 
      title = "Quiz"; 
      text = "Challenge yourself with intelligent quizzes."; 
      break;

    case "tracker": 
      title = "Daily Tracker"; 
      text = "Build consistent habits with reminders."; 
      break;

    case "favorites": 
      title = "Favorite Topics"; 
      text = "Save topics that inspire you."; 
      break;

    case "profile": 
      title = "Profile"; 
      text = "Your new profile has been created successfully!"; 
      break;

    case "start": 
      title = "Get Started"; 
      text = "Begin your mindful learning journey today."; 
      break;

    case "journey": 
      title = "Start Your Journey"; 
      text = "Take your first step towards mindful learning."; 
      break;

    case "features": 
      title = "Features"; 
      text = "Explore all ZenLearn features for effective learning."; 
      break;

    case "twitter": 
      title = "Twitter"; 
      text = "Follow ZenLearn on Twitter."; 
      break;

    case "github": 
      title = "GitHub"; 
      text = "Check out ZenLearn on GitHub."; 
      break;

    case "linkedin": 
      title = "LinkedIn"; 
      text = "Connect with ZenLearn on LinkedIn."; 
      break;

    default: 
      title = "ZenLearn"; 
      text = "Welcome to ZenLearn!";
  }

  document.getElementById("popup-title").innerText = title;
  document.getElementById("popup-text").innerText = text;
  document.getElementById("popup").style.display = "flex";
}

function closePopup() {
  document.getElementById("popup").style.display = "none";
}
// Video mute/unmute control
const video = document.getElementById("bgVideo");
const muteBtn = document.getElementById("muteBtn");

muteBtn.addEventListener("click", () => {
  video.muted = !video.muted;
  muteBtn.textContent = video.muted ? "🔇" : "🔊";
});
