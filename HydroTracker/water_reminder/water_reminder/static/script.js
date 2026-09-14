// Theme functionality
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);

    // Save to server
    fetch('/update_theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ theme: newTheme })
    });

    // Update theme icon
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Initialize theme icon
document.addEventListener('DOMContentLoaded', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
    }

    initializeCharts();
    setupReminders();
    checkOfflineStatus();
});

// Water intake functions
async function addWater(amount) {
    try {
        const response = await fetch('/add_water', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ amount: amount })
        });

        const data = await response.json();

        if (data.success) {
            updateProgress(data.total_today, data.progress_percentage);
            showNotification(`Added ${amount}ml of water! 💧`);

            // Add animation to progress circle
            const circle = document.querySelector('.circle');
            if (circle) {
                circle.classList.add('progress-update');
                setTimeout(() => circle.classList.remove('progress-update'), 500);
            }
        }
    } catch (error) {
        console.error('Error adding water:', error);
        showNotification('Error adding water intake', 'error');
    }
}

function addCustomWater() {
    const customAmount = document.getElementById('custom-amount');
    if (customAmount && customAmount.value > 0) {
        addWater(parseInt(customAmount.value));
        customAmount.value = '';
    } else {
        showNotification('Please enter a valid amount', 'error');
    }
}

async function updateGoal() {
    const goalInput = document.getElementById('daily-goal');
    const newGoal = goalInput ? goalInput.value : 2000;

    try {
        const response = await fetch('/update_goal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ goal: newGoal })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Daily goal updated! 🎯');
            // Update progress display with new goal
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    } catch (error) {
        console.error('Error updating goal:', error);
        showNotification('Error updating goal', 'error');
    }
}

function updateProgress(total, percentage) {
    // Update progress circle
    const circle = document.querySelector('.circle');
    const amountElement = document.querySelector('.amount');
    const goalElement = document.querySelector('.goal-text');

    if (circle) {
        circle.style.background = `conic-gradient(#667eea ${percentage * 3.6}deg, #e9ecef 0deg)`;
    }

    if (amountElement) {
        amountElement.textContent = `${total} ml`;
    }
}

// Chart initialization
function initializeCharts() {
    const weeklyChart = document.getElementById('weeklyChart');
    if (weeklyChart) {
        const ctx = weeklyChart.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Water Intake (ml)',
                    data: [1800, 2200, 1900, 2500, 2100, 2300, 2000],
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    borderRadius: 10,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'white'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'white'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }
}

// Smart reminder system
class SmartReminder {
    constructor() {
        this.peakHours = [9, 12, 15, 18, 21];
        this.reminderCount = 0;
        this.isActive = false;
    }

    calculateOptimalTimes() {
        const now = new Date();
        const currentHour = now.getHours();

        // Find next optimal reminder time
        const nextPeak = this.peakHours.find(hour => hour > currentHour) || this.peakHours[0];
        return nextPeak;
    }

    start() {
        if (this.isActive) return;

        this.isActive = true;
        this.scheduleSmartReminder();
    }

    stop() {
        this.isActive = false;
        if (this.reminderTimeout) {
            clearTimeout(this.reminderTimeout);
        }
    }

    scheduleSmartReminder() {
        if (!this.isActive) return;

        const nextTime = this.calculateOptimalTimes();
        const now = new Date();
        const targetTime = new Date();
        targetTime.setHours(nextTime, 0, 0, 0);

        let delay = targetTime - now;
        if (delay < 0) {
            delay += 24 * 60 * 60 * 1000; // Next day
        }

        this.reminderTimeout = setTimeout(() => {
            this.sendSmartReminder();
            this.reminderCount++;

            // Continue scheduling if still active
            if (this.isActive && this.reminderCount < 5) {
                this.scheduleSmartReminder();
            }
        }, delay);
    }

    sendSmartReminder() {
        if (Notification.permission === 'granted') {
            new Notification('💧 Time to Hydrate!', {
                body: `Stay hydrated! It's the perfect time to drink some water.`,
                tag: 'hydration-reminder'
            });

            // Also show in-app notification
            showNotification('💧 Reminder: Time to drink water!');
        }
    }
}

const smartReminder = new SmartReminder();

function setupReminders() {
    const toggle = document.getElementById('reminder-toggle');
    const intervalSelect = document.getElementById('reminder-interval');

    if (toggle && intervalSelect) {
        // Load saved settings
        const savedSettings = JSON.parse(localStorage.getItem('reminderSettings') || '{}');
        toggle.checked = savedSettings.enabled || false;
        intervalSelect.value = savedSettings.interval || '60';

        if (toggle.checked) {
            smartReminder.start();
        }

        toggle.addEventListener('change', function() {
            if (this.checked) {
                smartReminder.start();
            } else {
                smartReminder.stop();
            }
            saveReminderSettings();
        });

        intervalSelect.addEventListener('change', function() {
            if (toggle.checked) {
                smartReminder.stop();
                smartReminder.start();
            }
            saveReminderSettings();
        });
    }
}

function saveReminderSettings() {
    const toggle = document.getElementById('reminder-toggle');
    const intervalSelect = document.getElementById('reminder-interval');

    if (toggle && intervalSelect) {
        localStorage.setItem('reminderSettings', JSON.stringify({
            enabled: toggle.checked,
            interval: intervalSelect.value
        }));
    }
}

// Notification system
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type === 'error' ? 'error' : ''}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        border-radius: 10px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    `;

    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Offline functionality
function checkOfflineStatus() {
    if (!navigator.onLine) {
        showNotification('You are currently offline. Some features may be limited.', 'error');
    }

    window.addEventListener('online', () => {
        showNotification('Connection restored! 🎉');
    });

    window.addEventListener('offline', () => {
        showNotification('You are currently offline. Some features may be limited.', 'error');
    });
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    // Don't request immediately, wait for user interaction
    document.addEventListener('click', function initialNotificationRequest() {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
        document.removeEventListener('click', initialNotificationRequest);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                addWater(250);
                break;
            case '2':
                e.preventDefault();
                addWater(500);
                break;
            case '3':
                e.preventDefault();
                addWater(1000);
                break;
        }
    }
});