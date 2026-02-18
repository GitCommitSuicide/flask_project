// Main JavaScript file for FitLife

document.addEventListener("DOMContentLoaded", () => {
  // Mobile navigation toggle
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.toggle("active")
      hamburger.classList.toggle("active")
    })
  }

  // Auto-hide flash messages
  const flashMessages = document.querySelectorAll(".flash-message")
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      message.style.transform = "translateX(100%)"
      setTimeout(() => {
        message.remove()
      }, 300)
    }, 5000)
  })

  // Smooth scrolling for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]')
  anchorLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Form validation
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const requiredFields = form.querySelectorAll("[required]")
      let isValid = true

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          isValid = false
          field.style.borderColor = "#f44336"
          field.addEventListener("input", function () {
            this.style.borderColor = "#e9ecef"
          })
        }
      })

      if (!isValid) {
        e.preventDefault()
        showNotification("Please fill in all required fields", "error")
      }
    })
  })

  // Progress chart (if on dashboard)
  if (window.location.pathname === "/dashboard") {
    loadProgressChart()
  }

  // Animate elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in")
      }
    })
  }, observerOptions)

  const animateElements = document.querySelectorAll(".feature-card, .stat-card, .exercise-card, .pose-card, .meal-card")
  animateElements.forEach((el) => {
    observer.observe(el)
  })
})

// Utility functions
function showNotification(message, type = "success") {
  const notification = document.createElement("div")
  notification.className = `flash-message ${type}`
  notification.textContent = message

  const container = document.querySelector(".flash-messages") || createFlashContainer()
  container.appendChild(notification)

  setTimeout(() => {
    notification.style.opacity = "0"
    notification.style.transform = "translateX(100%)"
    setTimeout(() => {
      notification.remove()
    }, 300)
  }, 5000)
}

function createFlashContainer() {
  const container = document.createElement("div")
  container.className = "flash-messages"
  document.body.appendChild(container)
  return container
}

function loadProgressChart() {
  fetch("/progress_data")
    .then((response) => response.json())
    .then((data) => {
      if (data.dates && data.weights) {
        createProgressChart(data.dates, data.weights)
      }
    })
    .catch((error) => {
      console.error("Error loading progress data:", error)
    })
}

function createProgressChart(dates, weights) {
  // Simple chart implementation using CSS
  const chartContainer = document.querySelector(".progress-chart")
  if (!chartContainer) return

  const maxWeight = Math.max(...weights)
  const minWeight = Math.min(...weights)
  const range = maxWeight - minWeight || 1

  chartContainer.innerHTML = ""

  dates.forEach((date, index) => {
    const point = document.createElement("div")
    point.className = "chart-point"
    point.style.left = `${(index / (dates.length - 1)) * 100}%`
    point.style.bottom = `${((weights[index] - minWeight) / range) * 100}%`
    point.title = `${date}: ${weights[index]}kg`
    chartContainer.appendChild(point)
  })
}

// BMI Calculator
function calculateBMI(weight, height) {
  const heightInMeters = height / 100
  return weight / (heightInMeters * heightInMeters)
}

function getBMICategory(bmi) {
  if (bmi < 18.5) return "Underweight"
  if (bmi < 25) return "Normal weight"
  if (bmi < 30) return "Overweight"
  return "Obese"
}

// Calorie calculation helpers
function calculateCaloriesBurned(exercise, duration, weight = 70) {
  // Simplified calorie calculation
  const metValues = {
    running: 11.5,
    cycling: 8.0,
    swimming: 10.0,
    walking: 3.8,
    strength: 6.0,
    yoga: 3.0,
  }

  const met = metValues[exercise.toLowerCase()] || 5.0
  return Math.round(met * weight * (duration / 60))
}

// Local storage helpers
function saveToLocalStorage(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error("Error saving to localStorage:", error)
  }
}

function getFromLocalStorage(key) {
  try {
    const data = localStorage.getItem(key)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error("Error reading from localStorage:", error)
    return null
  }
}

// Workout timer functionality
const workoutTimer = {
  startTime: null,
  duration: 0,
  isRunning: false,
  interval: null,
}

function startWorkoutTimer() {
  if (!workoutTimer.isRunning) {
    workoutTimer.startTime = Date.now() - workoutTimer.duration
    workoutTimer.isRunning = true
    workoutTimer.interval = setInterval(updateWorkoutTimer, 1000)
  }
}

function pauseWorkoutTimer() {
  if (workoutTimer.isRunning) {
    clearInterval(workoutTimer.interval)
    workoutTimer.isRunning = false
  }
}

function resetWorkoutTimer() {
  clearInterval(workoutTimer.interval)
  workoutTimer.startTime = null
  workoutTimer.duration = 0
  workoutTimer.isRunning = false
  updateWorkoutTimerDisplay()
}

function updateWorkoutTimer() {
  if (workoutTimer.isRunning) {
    workoutTimer.duration = Date.now() - workoutTimer.startTime
    updateWorkoutTimerDisplay()
  }
}

function updateWorkoutTimerDisplay() {
  const timerDisplay = document.getElementById("workoutTimer")
  if (timerDisplay) {
    const minutes = Math.floor(workoutTimer.duration / 60000)
    const seconds = Math.floor((workoutTimer.duration % 60000) / 1000)
    timerDisplay.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
  }
}

// Exercise tracking
function trackExerciseCompletion(exerciseId, duration) {
  const completedExercises = getFromLocalStorage("completedExercises") || []
  const today = new Date().toISOString().split("T")[0]

  completedExercises.push({
    exerciseId: exerciseId,
    duration: duration,
    date: today,
    timestamp: Date.now(),
  })

  saveToLocalStorage("completedExercises", completedExercises)
}

// Goal progress tracking
function updateGoalProgress(type, value) {
  const progress = getFromLocalStorage("goalProgress") || {}
  const today = new Date().toISOString().split("T")[0]

  if (!progress[today]) {
    progress[today] = {}
  }

  progress[today][type] = value
  saveToLocalStorage("goalProgress", progress)
}

// Responsive image loading
function lazyLoadImages() {
  const images = document.querySelectorAll("img[data-src]")
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.classList.remove("lazy")
        imageObserver.unobserve(img)
      }
    })
  })

  images.forEach((img) => imageObserver.observe(img))
}

// Initialize lazy loading when DOM is ready
document.addEventListener("DOMContentLoaded", lazyLoadImages)

// Service Worker registration for offline functionality
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("ServiceWorker registration successful")
      })
      .catch((error) => {
        console.log("ServiceWorker registration failed")
      })
  })
}

// Dark mode toggle (optional feature)
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode")
  const isDarkMode = document.body.classList.contains("dark-mode")
  saveToLocalStorage("darkMode", isDarkMode)
}

// Load dark mode preference
document.addEventListener("DOMContentLoaded", () => {
  const darkMode = getFromLocalStorage("darkMode")
  if (darkMode) {
    document.body.classList.add("dark-mode")
  }
})

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + K to focus search
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault()
    const searchInput = document.querySelector('input[type="search"], .chat-input input')
    if (searchInput) {
      searchInput.focus()
    }
  }

  // Escape to close modals
  if (e.key === "Escape") {
    const openModals = document.querySelectorAll('.modal[style*="block"]')
    openModals.forEach((modal) => {
      modal.style.display = "none"
    })
  }
})
