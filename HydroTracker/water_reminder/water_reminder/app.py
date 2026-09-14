# from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
# import sqlite3
# from datetime import datetime, date, timedelta
# from database import init_db, get_db_connection, hash_password, check_password
# from email_service import email_service
# import atexit
# import threading
# import time
# import os
# from dotenv import load_dotenv
#
# # Load environment variables
# load_dotenv()
#
# app = Flask(__name__)
# app.secret_key = os.getenv('b030fef34c335a3a310284b659a85c11fa0bc1631b38ee9dfc62a2b69b8cef83', 'fallback-secret-key-for-development')
#
# # Email Configuration - ADD THIS SECTION
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # ✅ Correct
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # ✅ Correct
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('ashkolhe65@gmail.com'))
#
# # Debug email configuration
# print("=== EMAIL CONFIGURATION ===")
# print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
# print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
# print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
# print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
# print("MAIL_PASSWORD: [HIDDEN]" if app.config['MAIL_PASSWORD'] else "MAIL_PASSWORD: [MISSING]")
# print("===========================")
#
# # Initialize database
# print("Initializing database...")
# init_db()
# print("Database initialized successfully!")
#
#
# # Custom Jinja2 filters
# @app.template_filter('format_date')
# def format_date(value, format='%Y-%m-%d'):
#     if value is None:
#         return ''
#     if isinstance(value, str):
#         try:
#             return datetime.strptime(value, '%Y-%m-%d').strftime(format)
#         except ValueError:
#             return value[:10]
#     return value.strftime(format)
#
#
# @app.template_filter('format_datetime')
# def format_datetime(value, format='%Y-%m-%d %H:%M'):
#     if value is None:
#         return ''
#     if isinstance(value, str):
#         try:
#             return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
#         except ValueError:
#             return value[:16]
#     return value.strftime(format)
#
#
# # Background email scheduler
# class EmailScheduler:
#     def __init__(self):
#         self.is_running = False
#         self.thread = None
#
#     def start(self):
#         self.is_running = True
#         self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
#         self.thread.start()
#         print("📧 Email scheduler started")
#
#     def stop(self):
#         self.is_running = False
#         print("📧 Email scheduler stopped")
#
#     def _run_scheduler(self):
#         while self.is_running:
#             try:
#                 now = datetime.now()
#                 current_hour = now.hour
#                 current_minute = now.minute
#
#                 print(f"📧 Scheduler checking at {now.strftime('%H:%M')}")
#
#                 # Define reminder hours (8 AM to 10 PM, every 2 hours)
#                 reminder_hours = [8, 10, 12, 14, 16, 18, 20, 22]
#
#                 # Send reminders at the top of each hour in reminder_hours
#                 if current_minute == 0 and current_hour in reminder_hours:
#                     print(f"🕐 Sending reminder for {current_hour}:00...")
#                     self.send_daily_reminders()
#
#                 time.sleep(60)  # Check every minute
#             except Exception as e:
#                 print(f"❌ Error in email scheduler: {e}")
#                 time.sleep(60)
#
#     def send_daily_reminders(self):
#         try:
#             conn = get_db_connection()
#             users = conn.execute(
#                 'SELECT id, username, email FROM users WHERE email_notifications = 1 AND reminder_frequency = "daily"'
#             ).fetchall()
#             conn.close()
#
#             print(f"📧 Found {len(users)} users for daily reminders")
#
#             for user in users:
#                 try:
#                     print(f"📧 Sending daily reminder to {user['email']}")
#                     success = email_service.send_daily_reminder(user['id'])
#                     if success:
#                         print(f"✅ Daily reminder sent to user {user['id']}")
#                     else:
#                         print(f"❌ Failed to send daily reminder to user {user['id']}")
#                 except Exception as e:
#                     print(f"❌ Error sending daily reminder to user {user['id']}: {e}")
#         except Exception as e:
#             print(f"❌ Error in send_daily_reminders: {e}")
#
#     def send_goal_reminders(self):
#         try:
#             conn = get_db_connection()
#             users = conn.execute(
#                 'SELECT id, username, email FROM users WHERE email_notifications = 1'
#             ).fetchall()
#             conn.close()
#
#             print(f"📧 Found {len(users)} users for goal reminders")
#
#             for user in users:
#                 try:
#                     print(f"📧 Sending goal reminder to {user['email']}")
#                     success = email_service.send_goal_reminder(user['id'])
#                     if success:
#                         print(f"✅ Goal reminder sent to user {user['id']}")
#                     else:
#                         print(f"❌ Failed to send goal reminder to user {user['id']}")
#                 except Exception as e:
#                     print(f"❌ Error sending goal reminder to user {user['id']}: {e}")
#         except Exception as e:
#             print(f"❌ Error in send_goal_reminders: {e}")
#
#
# # Start email scheduler
# email_scheduler = EmailScheduler()
# email_scheduler.start()
#
#
# # Authentication decorators
# def login_required(f):
#     from functools import wraps
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             flash("Please login to access this page.", "error")
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#
#     return decorated_function
#
#
# # ===== TEST EMAIL ROUTE =====
#
# @app.route('/test-email-simple')
# def test_email_simple():
#     """Simple email test without authentication"""
#     try:
#         # Test basic email functionality
#         from flask_mail import Mail, Message
#         mail = Mail(app)
#
#         test_recipient = os.getenv('MAIL_USERNAME')  # Send to yourself for testing
#
#         if not test_recipient:
#             return "MAIL_USERNAME not set in environment variables"
#
#         msg = Message(
#             subject='🧪 HydroTracker Test Email',
#             recipients=[test_recipient],
#             body='This is a test email from HydroTracker. If you receive this, email configuration is working!',
#             html='<h2>🧪 HydroTracker Test Email</h2><p>This is a test email from HydroTracker. If you receive this, email configuration is working!</p>'
#         )
#
#         mail.send(msg)
#         return f"✅ Test email sent to {test_recipient}! Check your inbox."
#
#     except Exception as e:
#         return f"❌ Email test failed: {str(e)}"
#
#
#
#
# # ===== ROUTES =====
#
# @app.route('/')
# def index():
#     if 'user_id' in session:
#         return redirect(url_for('dashboard'))
#     return render_template('index.html')
#
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         daily_goal = request.form.get('daily_goal', 2000)
#         weight_kg = request.form.get('weight_kg')
#         activity_level = request.form.get('activity_level', 'moderate')
#
#         conn = get_db_connection()
#         try:
#             conn.execute(
#                 'INSERT INTO users (username, email, password, daily_goal, weight_kg, activity_level) VALUES (?, ?, ?, ?, ?, ?)',
#                 (username, email, hash_password(password), daily_goal, weight_kg, activity_level))
#             conn.commit()
#
#             # Get user ID for session
#             user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             session['theme'] = user['theme']
#
#             # Send welcome email
#             try:
#                 email_service.send_welcome_email(user['id'])
#             except Exception as e:
#                 print(f"❌ Welcome email failed: {e}")
#
#             flash('Registration successful! Welcome to HydroTracker.', 'success')
#             return redirect(url_for('dashboard'))
#         except sqlite3.IntegrityError:
#             flash('Username or email already exists.', 'error')
#         finally:
#             conn.close()
#
#     return render_template('index.html', register=True)
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
#         conn.close()
#
#         if user and check_password(password, user['password']):
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             session['theme'] = user['theme']
#             flash(f'Welcome back, {user["username"]}!', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid credentials. Please try again.', 'error')
#
#     return render_template('index.html', login=True)
#
#
# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out successfully.', 'info')
#     return redirect(url_for('index'))
#
#
# @app.route('/dashboard')
# @login_required
# def dashboard():
#     user_id = session['user_id']
#     conn = get_db_connection()
#
#     # Get user info
#     user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#
#     if user is None:
#         conn.close()
#         session.clear()
#         return redirect(url_for('login'))
#
#     today_str = date.today().isoformat()
#
#     # Get today's water intake
#     today_intake = conn.execute('''
#         SELECT SUM(amount) as total FROM water_intake
#         WHERE user_id = ? AND date(timestamp) = date(?)
#     ''', (user_id, today_str)).fetchone()
#
#     # Get recent intake history
#     recent_intake_raw = conn.execute('''
#         SELECT amount, timestamp FROM water_intake
#         WHERE user_id = ? AND date(timestamp) = date(?)
#         ORDER BY timestamp DESC
#         LIMIT 5
#     ''', (user_id, today_str)).fetchall()
#
#     recent_intake = []
#     for intake in recent_intake_raw:
#         recent_intake.append({
#             'amount': intake['amount'],
#             'timestamp': intake['timestamp'].strftime('%H:%M') if intake['timestamp'] else 'N/A'
#         })
#
#     # Get weekly progress
#     week_start = date.today() - timedelta(days=date.today().weekday())
#     weekly_data = []
#     for i in range(7):
#         day = week_start + timedelta(days=i)
#         day_str = day.isoformat()
#         day_intake = conn.execute('''
#             SELECT SUM(amount) as total FROM water_intake
#             WHERE user_id = ? AND date(timestamp) = date(?)
#         ''', (user_id, day_str)).fetchone()
#         weekly_data.append({
#             'day': day.strftime('%a'),
#             'total': day_intake['total'] or 0,
#             'date': day.strftime('%Y-%m-%d')
#         })
#
#     # Check and unlock achievements
#     check_achievements(user_id, conn)
#
#     # Get user achievements
#     achievements_raw = conn.execute('''
#         SELECT a.* FROM achievements a
#         JOIN user_achievements ua ON a.id = ua.achievement_id
#         WHERE ua.user_id = ?
#         ORDER BY ua.unlocked_at DESC
#         LIMIT 3
#     ''', (user_id,)).fetchall()
#
#     achievements = []
#     for achievement in achievements_raw:
#         achievements.append({
#             'id': achievement['id'],
#             'name': achievement['name'],
#             'description': achievement['description'],
#             'icon': achievement['icon'],
#             'condition': achievement['condition']
#         })
#
#     conn.close()
#
#     total_today = today_intake['total'] or 0
#     daily_goal = user['daily_goal'] or 2000
#     progress_percentage = min((total_today / daily_goal) * 100, 100)
#
#     # Get weather-based recommendation
#     weather_recommendation = get_weather_based_recommendation()
#
#     return render_template('dashboard.html',
#                            user=user,
#                            total_today=total_today,
#                            progress_percentage=progress_percentage,
#                            recent_intake=recent_intake,
#                            weekly_data=weekly_data,
#                            achievements=achievements,
#                            weather_recommendation=weather_recommendation)
#
#
# @app.route('/add_water', methods=['POST'])
# @login_required
# def add_water():
#     try:
#         data = request.get_json()
#         amount = data.get('amount')
#         user_id = session['user_id']
#
#         # Convert to integer first, then validate
#         if not amount:
#             return jsonify({'success': False, 'error': 'Amount is required'})
#
#         try:
#             amount_int = int(amount)
#         except (ValueError, TypeError):
#             return jsonify({'success': False, 'error': 'Amount must be a valid number'})
#
#         if amount_int <= 0:
#             return jsonify({'success': False, 'error': 'Amount must be greater than 0'})
#
#         if amount_int > 1000:
#             return jsonify({'success': False, 'error': 'Amount must be reasonable (max 1000ml per entry)'})
#
#         conn = get_db_connection()
#         conn.execute('INSERT INTO water_intake (user_id, amount) VALUES (?, ?)',
#                      (user_id, amount_int))
#         conn.commit()
#
#         # Check for new achievements
#         check_achievements(user_id, conn)
#
#         # Get updated total
#         today_str = date.today().isoformat()
#         today_intake = conn.execute('''
#             SELECT SUM(amount) as total FROM water_intake
#             WHERE user_id = ? AND date(timestamp) = date(?)
#         ''', (user_id, today_str)).fetchone()
#
#         user = conn.execute('SELECT daily_goal FROM users WHERE id = ?', (user_id,)).fetchone()
#         conn.close()
#
#         total_today = today_intake['total'] or 0
#         daily_goal = user['daily_goal'] or 2000
#         progress_percentage = min((total_today / daily_goal) * 100, 100)
#
#         return jsonify({
#             'success': True,
#             'total_today': total_today,
#             'progress_percentage': progress_percentage
#         })
#
#     except Exception as e:
#         return jsonify({'success': False, 'error': f'Failed to add water: {str(e)}'})
#
#
# @app.route('/history')
# @login_required
# def history():
#     user_id = session['user_id']
#     conn = get_db_connection()
#
#     history_raw = conn.execute('''
#         SELECT DATE(timestamp) as date, SUM(amount) as total
#         FROM water_intake
#         WHERE user_id = ?
#         GROUP BY DATE(timestamp)
#         ORDER BY date DESC
#         LIMIT 30
#     ''', (user_id,)).fetchall()
#
#     history = []
#     for row in history_raw:
#         history.append({
#             'date': row['date'],
#             'total': row['total'] or 0
#         })
#
#     conn.close()
#     return render_template('history.html', history=history)
#
#
# @app.route('/analytics')
# @login_required
# def analytics():
#     """User analytics page"""
#     user_id = session['user_id']
#     conn = get_db_connection()
#
#     # Weekly data
#     weekly_data_raw = conn.execute('''
#         SELECT DATE(timestamp) as date, SUM(amount) as total
#         FROM water_intake
#         WHERE user_id = ? AND timestamp >= date('now', '-7 days')
#         GROUP BY DATE(timestamp)
#         ORDER BY date
#     ''', (user_id,)).fetchall()
#
#     # Format weekly data
#     weekly_data = []
#     for row in weekly_data_raw:
#         date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date() if isinstance(row['date'], str) else row['date']
#         weekly_data.append({
#             'date': date_obj.strftime('%Y-%m-%d'),
#             'total': row['total'] or 0,
#             'day': date_obj.strftime('%a')
#         })
#
#     # Monthly summary
#     monthly_summary_result = conn.execute('''
#         SELECT
#             COUNT(*) as days_logged,
#             AVG(total) as avg_daily,
#             MAX(total) as max_daily,
#             SUM(total) as monthly_total
#         FROM (
#             SELECT DATE(timestamp) as date, SUM(amount) as total
#             FROM water_intake
#             WHERE user_id = ? AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
#             GROUP BY DATE(timestamp)
#         )
#     ''', (user_id,)).fetchone()
#
#     # Convert monthly summary to dictionary
#     monthly_summary = {
#         'days_logged': monthly_summary_result['days_logged'] or 0,
#         'avg_daily': round(monthly_summary_result['avg_daily'] or 0, 1),
#         'max_daily': monthly_summary_result['max_daily'] or 0,
#         'monthly_total': monthly_summary_result['monthly_total'] or 0
#     }
#
#     # Calculate streak
#     dates_data = conn.execute('''
#         SELECT DATE(timestamp) as date, SUM(amount) as total
#         FROM water_intake
#         WHERE user_id = ?
#         GROUP BY DATE(timestamp)
#         ORDER BY date DESC
#     ''', (user_id,)).fetchall()
#
#     # Calculate streak in Python
#     best_streak_value = 0
#     temp_streak = 0
#
#     for day_data in dates_data:
#         total_amount = day_data['total'] or 0
#         if total_amount >= 2000:
#             temp_streak += 1
#             best_streak_value = max(best_streak_value, temp_streak)
#         else:
#             temp_streak = 0
#
#     best_streak = {'best_streak': best_streak_value}
#
#     conn.close()
#
#     return render_template('analytics.html',
#                            weekly_data=weekly_data,
#                            monthly_summary=monthly_summary,
#                            best_streak=best_streak)
#
#
# @app.route('/achievements')
# @login_required
# def achievements():
#     user_id = session['user_id']
#     conn = get_db_connection()
#
#     achievements_raw = conn.execute('''
#         SELECT a.*,
#                CASE WHEN ua.user_id IS NOT NULL THEN 1 ELSE 0 END as unlocked,
#                ua.unlocked_at
#         FROM achievements a
#         LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
#         ORDER BY a.id
#     ''', (user_id,)).fetchall()
#
#     achievements = []
#     for row in achievements_raw:
#         achievements.append({
#             'id': row['id'],
#             'name': row['name'],
#             'description': row['description'],
#             'icon': row['icon'],
#             'condition': row['condition'],
#             'unlocked': bool(row['unlocked']),
#             'unlocked_at': row['unlocked_at']
#         })
#
#     conn.close()
#     return render_template('achievements.html', achievements=achievements)
#
#
# @app.route('/settings')
# @login_required
# def settings():
#     user_id = session['user_id']
#     conn = get_db_connection()
#     user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#     conn.close()
#
#     if user is None:
#         session.clear()
#         return redirect(url_for('login'))
#
#     return render_template('settings.html', user=user)
#
#
# @app.route('/update_goal', methods=['POST'])
# @login_required
# def update_goal():
#     try:
#         data = request.get_json()
#         new_goal = data.get('goal')
#
#         # Convert to integer first, then validate
#         if not new_goal:
#             return jsonify({'success': False, 'error': 'Goal is required'})
#
#         try:
#             new_goal_int = int(new_goal)
#         except (ValueError, TypeError):
#             return jsonify({'success': False, 'error': 'Goal must be a valid number'})
#
#         # Now compare the integer value
#         if new_goal_int <= 0:
#             return jsonify({'success': False, 'error': 'Goal must be greater than 0'})
#
#         if new_goal_int > 10000:  # Reasonable upper limit
#             return jsonify({'success': False, 'error': 'Goal must be less than 10000ml'})
#
#         # Update user's goal in database
#         user_id = session['user_id']
#         conn = get_db_connection()
#         conn.execute('UPDATE users SET daily_goal = ? WHERE id = ?', (new_goal_int, user_id))
#         conn.commit()
#         conn.close()
#
#         return jsonify({'success': True, 'message': 'Goal updated successfully'})
#
#     except Exception as e:
#         return jsonify({'success': False, 'error': f'Failed to update goal: {str(e)}'})
#
#
#
# @app.route('/update_theme', methods=['POST'])
# @login_required
# def update_theme():
#     theme = request.json.get('theme')
#     user_id = session['user_id']
#
#     conn = get_db_connection()
#     conn.execute('UPDATE users SET theme = ? WHERE id = ?', (theme, user_id))
#     conn.commit()
#     conn.close()
#
#     session['theme'] = theme
#     return jsonify({'success': True})
#
#
#
#
# @app.route('/update_email_settings', methods=['POST'])
# @login_required
# def update_email_settings():
#     email_notifications = request.json.get('email_notifications', 0)
#     reminder_frequency = request.json.get('reminder_frequency', 'daily')
#     user_id = session['user_id']
#
#     conn = get_db_connection()
#     conn.execute(
#         'UPDATE users SET email_notifications = ?, reminder_frequency = ? WHERE id = ?',
#         (email_notifications, reminder_frequency, user_id)
#     )
#     conn.commit()
#     conn.close()
#
#     return jsonify({'success': True})
#
#
# # ===== SMARTWATCH API ROUTES =====
#
# @app.route('/api/watch/status')
# @login_required
# def watch_status():
#     """Simple status for smartwatch"""
#     user_id = session['user_id']
#     conn = get_db_connection()
#
#     today_str = date.today().isoformat()
#     today_intake = conn.execute('''
#         SELECT SUM(amount) as total FROM water_intake
#         WHERE user_id = ? AND date(timestamp) = date(?)
#     ''', (user_id, today_str)).fetchone()
#
#     user = conn.execute('SELECT daily_goal FROM users WHERE id = ?', (user_id,)).fetchone()
#     conn.close()
#
#     total_today = today_intake['total'] or 0
#     daily_goal = user['daily_goal'] or 2000
#
#     return jsonify({
#         'current': total_today,
#         'goal': daily_goal,
#         'percent': min((total_today / daily_goal) * 100, 100),
#         'message': f'{total_today}ml / {daily_goal}ml'
#     })
#
#
# @app.route('/api/watch/log', methods=['POST'])
# @login_required
# def watch_log():
#     """Simple log from smartwatch"""
#     try:
#         user_id = session['user_id']
#         amount = request.json.get('amount', 250)
#
#         # Convert to integer first
#         try:
#             amount_int = int(amount)
#         except (ValueError, TypeError):
#             return jsonify({'success': False, 'error': 'Amount must be a valid number'})
#
#         if amount_int <= 0:
#             return jsonify({'success': False, 'error': 'Invalid amount'})
#
#         conn = get_db_connection()
#         conn.execute(
#             'INSERT INTO water_intake (user_id, amount) VALUES (?, ?)',
#             (user_id, amount_int)
#         )
#         conn.commit()
#
#         today_str = date.today().isoformat()
#         today_intake = conn.execute('''
#             SELECT SUM(amount) as total FROM water_intake
#             WHERE user_id = ? AND date(timestamp) = date(?)
#         ''', (user_id, today_str)).fetchone()
#         conn.close()
#
#         total_today = today_intake['total'] or 0
#
#         return jsonify({
#             'success': True,
#             'message': f'Logged {amount_int}ml',
#             'total_today': total_today
#         })
#     except Exception as e:
#         return jsonify({'success': False, 'error': f'Failed to log water: {str(e)}'})
#
# @app.route('/api/watch/quick/<int:amount>')
# @login_required
# def watch_quick_log(amount):
#     """Ultra-simple logging via URL - for watch browser"""
#     user_id = session['user_id']
#
#     if amount <= 0:
#         return "Invalid amount"
#
#     conn = get_db_connection()
#     conn.execute(
#         'INSERT INTO water_intake (user_id, amount) VALUES (?, ?)',
#         (user_id, amount)
#     )
#     conn.commit()
#     conn.close()
#
#     return f"""
#     <html>
#     <head>
#         <title>Water Logged</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <style>
#             body {{
#                 font-family: Arial, sans-serif;
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 color: white;
#                 text-align: center;
#                 padding: 2rem;
#                 margin: 0;
#             }}
#             .container {{
#                 background: rgba(255,255,255,0.1);
#                 padding: 2rem;
#                 border-radius: 20px;
#                 backdrop-filter: blur(10px);
#             }}
#             .success {{ font-size: 3rem; margin: 1rem 0; }}
#             .message {{ font-size: 1.5rem; margin: 1rem 0; }}
#             .button {{
#                 display: inline-block;
#                 background: white;
#                 color: #667eea;
#                 padding: 1rem 2rem;
#                 border-radius: 10px;
#                 text-decoration: none;
#                 margin: 0.5rem;
#                 font-weight: bold;
#             }}
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="success">✅</div>
#             <div class="message">Logged {amount}ml successfully!</div>
#             <div>
#                 <a href="/watch" class="button">Back to Watch</a>
#                 <a href="/dashboard" class="button">Dashboard</a>
#             </div>
#         </div>
#     </body>
#     </html>
#     """
#
#
# @app.route('/api/watch/history')
# @login_required
# def watch_history():
#     """Get recent history for smartwatch"""
#     user_id = session['user_id']
#     conn = get_db_connection()
#
#     recent = conn.execute('''
#         SELECT amount, timestamp
#         FROM water_intake
#         WHERE user_id = ?
#         ORDER BY timestamp DESC
#         LIMIT 10
#     ''', (user_id,)).fetchall()
#
#     conn.close()
#
#     logs = []
#     for log in recent:
#         timestamp_str = log['timestamp'].strftime('%H:%M') if hasattr(log['timestamp'], 'strftime') else log[
#                                                                                                              'timestamp'][
#                                                                                                          11:16]
#         logs.append({
#             'amount': log['amount'],
#             'time': timestamp_str
#         })
#
#     return jsonify({'recent_logs': logs})
#
#
# @app.route('/watch')
# @login_required
# def watch_setup():
#     """Smartwatch setup page"""
#     return render_template('watch_setup.html')
#
#
# # ===== HELPER FUNCTIONS =====
#
# def check_achievements(user_id, conn):
#     # Check first log achievement
#     first_log = conn.execute('''
#         SELECT COUNT(*) as count FROM water_intake WHERE user_id = ?
#     ''', (user_id,)).fetchone()
#
#     if first_log['count'] == 1:
#         unlock_achievement(user_id, 1, conn)
#
#     # Check overachiever achievement
#     max_daily = conn.execute('''
#         SELECT SUM(amount) as total FROM water_intake
#         WHERE user_id = ?
#         GROUP BY DATE(timestamp)
#         ORDER BY total DESC LIMIT 1
#     ''', (user_id,)).fetchone()
#
#     if max_daily and max_daily['total'] >= 3000:
#         unlock_achievement(user_id, 4, conn)
#
#     # Check streak achievements
#     current_streak = calculate_streak(user_id, conn)
#     if current_streak >= 3:
#         unlock_achievement(user_id, 2, conn)
#     if current_streak >= 7:
#         unlock_achievement(user_id, 3, conn)
#
#
# def unlock_achievement(user_id, achievement_id, conn):
#     try:
#         # Check if already unlocked
#         existing = conn.execute('''
#             SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = ?
#         ''', (user_id, achievement_id)).fetchone()
#
#         if not existing:
#             conn.execute('INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)',
#                          (user_id, achievement_id))
#             conn.commit()
#
#             # Send achievement email
#             achievement = conn.execute(
#                 'SELECT * FROM achievements WHERE id = ?', (achievement_id,)
#             ).fetchone()
#
#             if achievement:
#                 print(f"🎉 Achievement unlocked: {achievement['name']} for user {user_id}")
#                 threading.Thread(
#                     target=email_service.send_achievement_unlocked,
#                     args=(user_id, achievement)
#                 ).start()
#
#     except Exception as e:
#         print(f"❌ Error unlocking achievement: {e}")
#
#
# def calculate_streak(user_id, conn):
#     dates = conn.execute('''
#         SELECT DATE(timestamp) as date, SUM(amount) as total
#         FROM water_intake
#         WHERE user_id = ?
#         GROUP BY DATE(timestamp)
#         ORDER BY date DESC
#     ''', (user_id,)).fetchall()
#
#     streak = 0
#     today = date.today()
#
#     for i, day_data in enumerate(dates):
#         try:
#             if isinstance(day_data['date'], str):
#                 day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
#             else:
#                 day_date = day_data['date']
#         except (ValueError, TypeError):
#             continue
#
#         expected_date = today - timedelta(days=i)
#
#         if day_date == expected_date and day_data['total'] >= 2000:
#             streak += 1
#         else:
#             break
#
#     return streak
#
#
# def get_weather_based_recommendation():
#     try:
#         base_goal = 2000
#         base_goal += 300  # Simulate hot weather
#         return base_goal
#     except:
#         return 2300
#
#
# # Stop scheduler when app exits
# atexit.register(lambda: email_scheduler.stop())
#
# if __name__ == '__main__':
#     print("🚀 Starting HydroTracker Flask application...")
#     print("📧 Test email routes:")
#     print("   - /test-email-simple (no login required)")
#     app.run(debug=True)





from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime, date, timedelta
from database import db, init_db, hash_password, check_password
from email_service import email_service
import atexit
import threading
import time
import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

# Debug email configuration
print("=== EMAIL CONFIGURATION ===")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
print("MAIL_PASSWORD: [HIDDEN]" if app.config['MAIL_PASSWORD'] else "MAIL_PASSWORD: [MISSING]")
print("===========================")

# Initialize database
print("Initializing database...")
init_db()
print("Database initialized successfully!")

# Custom Jinja2 filters
@app.template_filter('format_date')
def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').strftime(format)
        except ValueError:
            return value[:10]
    return value.strftime(format)

@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
        except ValueError:
            return value[:16]
    return value.strftime(format)

# Background email scheduler
class EmailScheduler:
    def __init__(self):
        self.is_running = False
        self.thread = None

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("📧 Email scheduler started")

    def stop(self):
        self.is_running = False
        print("📧 Email scheduler stopped")

    def _run_scheduler(self):
        while self.is_running:
            try:
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute

                print(f"📧 Scheduler checking at {now.strftime('%H:%M')}")

                # Define reminder hours (8 AM to 10 PM, every 2 hours)
                reminder_hours = [8, 10, 12, 14, 16, 18, 20, 22]

                # Send reminders at the top of each hour in reminder_hours
                if current_minute == 0 and current_hour in reminder_hours:
                    print(f"🕐 Sending reminder for {current_hour}:00...")
                    self.send_daily_reminders()

                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Error in email scheduler: {e}")
                time.sleep(60)

    def send_daily_reminders(self):
        try:
            users = db.execute_query(
                'SELECT id, username, email FROM users WHERE email_notifications = 1 AND reminder_frequency = "daily"',
                fetch=True
            )

            print(f"📧 Found {len(users) if users else 0} users for daily reminders")

            if users:
                for user in users:
                    try:
                        print(f"📧 Sending daily reminder to {user['email']}")
                        success = email_service.send_daily_reminder(user['id'])
                        if success:
                            print(f"✅ Daily reminder sent to user {user['id']}")
                        else:
                            print(f"❌ Failed to send daily reminder to user {user['id']}")
                    except Exception as e:
                        print(f"❌ Error sending daily reminder to user {user['id']}: {e}")
        except Exception as e:
            print(f"❌ Error in send_daily_reminders: {e}")

    def send_goal_reminders(self):
        try:
            users = db.execute_query(
                'SELECT id, username, email FROM users WHERE email_notifications = 1',
                fetch=True
            )

            print(f"📧 Found {len(users) if users else 0} users for goal reminders")

            if users:
                for user in users:
                    try:
                        print(f"📧 Sending goal reminder to {user['email']}")
                        success = email_service.send_goal_reminder(user['id'])
                        if success:
                            print(f"✅ Goal reminder sent to user {user['id']}")
                        else:
                            print(f"❌ Failed to send goal reminder to user {user['id']}")
                    except Exception as e:
                        print(f"❌ Error sending goal reminder to user {user['id']}: {e}")
        except Exception as e:
            print(f"❌ Error in send_goal_reminders: {e}")

# Start email scheduler
email_scheduler = EmailScheduler()
email_scheduler.start()

# Authentication decorators
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== TEST EMAIL ROUTE =====
@app.route('/test-email-simple')
def test_email_simple():
    """Simple email test without authentication"""
    try:
        # Test basic email functionality
        from flask_mail import Mail, Message
        mail = Mail(app)

        test_recipient = os.getenv('MAIL_USERNAME')  # Send to yourself for testing

        if not test_recipient:
            return "MAIL_USERNAME not set in environment variables"

        msg = Message(
            subject='🧪 HydroTracker Test Email',
            recipients=[test_recipient],
            body='This is a test email from HydroTracker. If you receive this, email configuration is working!',
            html='<h2>🧪 HydroTracker Test Email</h2><p>This is a test email from HydroTracker. If you receive this, email configuration is working!</p>'
        )

        mail.send(msg)
        return f"✅ Test email sent to {test_recipient}! Check your inbox."

    except Exception as e:
        return f"❌ Email test failed: {str(e)}"

# ===== ROUTES =====
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        daily_goal = request.form.get('daily_goal', 2000)
        weight_kg = request.form.get('weight_kg')
        activity_level = request.form.get('activity_level', 'moderate')

        try:
            # Insert user
            user_id = db.execute_query(
                'INSERT INTO users (username, email, password, daily_goal, weight_kg, activity_level) VALUES (%s, %s, %s, %s, %s, %s)',
                (username, email, hash_password(password), daily_goal, weight_kg, activity_level)
            )

            if user_id:
                # Get user for session
                user = db.execute_one('SELECT * FROM users WHERE id = %s', (user_id,))
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['theme'] = user['theme']

                # Send welcome email
                try:
                    email_service.send_welcome_email(user['id'])
                except Exception as e:
                    print(f"❌ Welcome email failed: {e}")

                flash('Registration successful! Welcome to HydroTracker.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
        except mysql.connector.IntegrityError:
            flash('Username or email already exists.', 'error')
        except Exception as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration.', 'error')

    return render_template('index.html', register=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.execute_one('SELECT * FROM users WHERE username = %s', (username,))

        if user and check_password(password, user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['theme'] = user['theme']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('index.html', login=True)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']

    # Get user info
    user = db.execute_one('SELECT * FROM users WHERE id = %s', (user_id,))

    if user is None:
        session.clear()
        return redirect(url_for('login'))

    today_str = date.today().isoformat()

    # Get today's water intake
    today_intake = db.execute_one('''
        SELECT SUM(amount) as total FROM water_intake 
        WHERE user_id = %s AND DATE(timestamp) = DATE(%s)
    ''', (user_id, today_str))

    # Get recent intake history
    recent_intake_raw = db.execute_query('''
        SELECT amount, timestamp FROM water_intake 
        WHERE user_id = %s AND DATE(timestamp) = DATE(%s)
        ORDER BY timestamp DESC
        LIMIT 5
    ''', (user_id, today_str), fetch=True)

    recent_intake = []
    if recent_intake_raw:
        for intake in recent_intake_raw:
            recent_intake.append({
                'amount': intake['amount'],
                'timestamp': intake['timestamp'].strftime('%H:%M') if intake['timestamp'] else 'N/A'
            })

    # Get weekly progress
    week_start = date.today() - timedelta(days=date.today().weekday())
    weekly_data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.isoformat()
        day_intake = db.execute_one('''
            SELECT SUM(amount) as total FROM water_intake 
            WHERE user_id = %s AND DATE(timestamp) = DATE(%s)
        ''', (user_id, day_str))
        weekly_data.append({
            'day': day.strftime('%a'),
            'total': day_intake['total'] or 0 if day_intake else 0,
            'date': day.strftime('%Y-%m-%d')
        })

    # Check and unlock achievements
    check_achievements(user_id)

    # Get user achievements
    achievements_raw = db.execute_query('''
        SELECT a.* FROM achievements a
        JOIN user_achievements ua ON a.id = ua.achievement_id
        WHERE ua.user_id = %s
        ORDER BY ua.unlocked_at DESC
        LIMIT 3
    ''', (user_id,), fetch=True)

    achievements = []
    if achievements_raw:
        for achievement in achievements_raw:
            achievements.append({
                'id': achievement['id'],
                'name': achievement['name'],
                'description': achievement['description'],
                'icon': achievement['icon'],
                'condition': achievement['condition']
            })

    total_today = today_intake['total'] or 0 if today_intake else 0
    daily_goal = user['daily_goal'] or 2000
    # progress_percentage = min((total_today / daily_goal) * 100, 100) if daily_goal > 0 else 0
    progress_percentage = float(min((total_today / daily_goal) * 100, 100))if daily_goal > 0 else 0
 



    # Get weather-based recommendation
    weather_recommendation = get_weather_based_recommendation()

    return render_template('dashboard.html',
                           user=user,
                           total_today=total_today,
                           progress_percentage=progress_percentage,
                           recent_intake=recent_intake,
                           weekly_data=weekly_data,
                           achievements=achievements,
                           weather_recommendation=weather_recommendation)

@app.route('/add_water', methods=['POST'])
@login_required
def add_water():
    try:
        data = request.get_json()
        amount = data.get('amount')
        user_id = session['user_id']

        # Convert to integer first, then validate
        if not amount:
            return jsonify({'success': False, 'error': 'Amount is required'})

        try:
            amount_int = int(amount)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Amount must be a valid number'})

        if amount_int <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than 0'})

        if amount_int > 1000:
            return jsonify({'success': False, 'error': 'Amount must be reasonable (max 1000ml per entry)'})

        # Insert water intake
        result = db.execute_query(
            'INSERT INTO water_intake (user_id, amount) VALUES (%s, %s)',
            (user_id, amount_int)
        )

        if not result:
            return jsonify({'success': False, 'error': 'Failed to save water intake'})

        # Check for new achievements
        check_achievements(user_id)

        # Get updated total
        today_str = date.today().isoformat()
        today_intake = db.execute_one('''
            SELECT SUM(amount) as total FROM water_intake 
            WHERE user_id = %s AND DATE(timestamp) = DATE(%s)
        ''', (user_id, today_str))

        user = db.execute_one('SELECT daily_goal FROM users WHERE id = %s', (user_id,))

        total_today = today_intake['total'] or 0 if today_intake else 0
        daily_goal = user['daily_goal'] or 2000 if user else 2000
        progress_percentage = min((total_today / daily_goal) * 100, 100)

        return jsonify({
            'success': True,
            'total_today': total_today,
            'progress_percentage': progress_percentage
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to add water: {str(e)}'})

@app.route('/history')
@login_required
def history():
    user_id = session['user_id']

    history_raw = db.execute_query('''
        SELECT DATE(timestamp) as date, SUM(amount) as total 
        FROM water_intake 
        WHERE user_id = %s 
        GROUP BY DATE(timestamp) 
        ORDER BY date DESC
        LIMIT 30
    ''', (user_id,), fetch=True)

    history = []
    if history_raw:
        for row in history_raw:
            history.append({
                'date': row['date'],
                'total': row['total'] or 0
            })

    return render_template('history.html', history=history)

@app.route('/analytics')
@login_required
def analytics():
    """User analytics page"""
    user_id = session['user_id']

    # Weekly data
    weekly_data_raw = db.execute_query('''
        SELECT DATE(timestamp) as date, SUM(amount) as total 
        FROM water_intake 
        WHERE user_id = %s AND timestamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(timestamp) 
        ORDER BY date
    ''', (user_id,), fetch=True)

    # Format weekly data
    weekly_data = []
    if weekly_data_raw:
        for row in weekly_data_raw:
            date_obj = datetime.strptime(str(row['date']), '%Y-%m-%d').date() if isinstance(row['date'], str) else row['date']
            weekly_data.append({
                'date': date_obj.strftime('%Y-%m-%d'),
                'total': row['total'] or 0,
                'day': date_obj.strftime('%a')
            })

    # Monthly summary
    monthly_summary_result = db.execute_one('''
        SELECT 
            COUNT(*) as days_logged,
            AVG(total) as avg_daily,
            MAX(total) as max_daily,
            SUM(total) as monthly_total
        FROM (
            SELECT DATE(timestamp) as date, SUM(amount) as total 
            FROM water_intake 
            WHERE user_id = %s AND MONTH(timestamp) = MONTH(CURDATE()) AND YEAR(timestamp) = YEAR(CURDATE())
            GROUP BY DATE(timestamp)
        ) as daily_totals
    ''', (user_id,))

    # Convert monthly summary to dictionary
    monthly_summary = {
        'days_logged': monthly_summary_result['days_logged'] or 0 if monthly_summary_result else 0,
        'avg_daily': round(monthly_summary_result['avg_daily'] or 0, 1) if monthly_summary_result else 0,
        'max_daily': monthly_summary_result['max_daily'] or 0 if monthly_summary_result else 0,
        'monthly_total': monthly_summary_result['monthly_total'] or 0 if monthly_summary_result else 0
    }

    # Calculate streak
    dates_data = db.execute_query('''
        SELECT DATE(timestamp) as date, SUM(amount) as total 
        FROM water_intake 
        WHERE user_id = %s 
        GROUP BY DATE(timestamp) 
        ORDER BY date DESC
    ''', (user_id,), fetch=True)

    # Calculate streak in Python
    best_streak_value = 0
    temp_streak = 0

    if dates_data:
        for day_data in dates_data:
            total_amount = day_data['total'] or 0
            if total_amount >= 2000:
                temp_streak += 1
                best_streak_value = max(best_streak_value, temp_streak)
            else:
                temp_streak = 0

    best_streak = {'best_streak': best_streak_value}

    return render_template('analytics.html',
                           weekly_data=weekly_data,
                           monthly_summary=monthly_summary,
                           best_streak=best_streak)

@app.route('/achievements')
@login_required
def achievements():
    user_id = session['user_id']

    achievements_raw = db.execute_query('''
        SELECT a.*, 
               CASE WHEN ua.user_id IS NOT NULL THEN 1 ELSE 0 END as unlocked,
               ua.unlocked_at
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = %s
        ORDER BY a.id
    ''', (user_id,), fetch=True)

    achievements = []
    if achievements_raw:
        for row in achievements_raw:
            achievements.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'icon': row['icon'],
                'condition': row['condition'],
                'unlocked': bool(row['unlocked']),
                'unlocked_at': row['unlocked_at']
            })

    return render_template('achievements.html', achievements=achievements)

@app.route('/settings')
@login_required
def settings():
    user_id = session['user_id']
    user = db.execute_one('SELECT * FROM users WHERE id = %s', (user_id,))

    if user is None:
        session.clear()
        return redirect(url_for('login'))

    return render_template('settings.html', user=user)

@app.route('/update_goal', methods=['POST'])
@login_required
def update_goal():
    try:
        data = request.get_json()
        new_goal = data.get('goal')

        # Convert to integer first, then validate
        if not new_goal:
            return jsonify({'success': False, 'error': 'Goal is required'})

        try:
            new_goal_int = int(new_goal)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Goal must be a valid number'})

        # Now compare the integer value
        if new_goal_int <= 0:
            return jsonify({'success': False, 'error': 'Goal must be greater than 0'})

        if new_goal_int > 10000:  # Reasonable upper limit
            return jsonify({'success': False, 'error': 'Goal must be less than 10000ml'})

        # Update user's goal in database
        user_id = session['user_id']
        result = db.execute_query(
            'UPDATE users SET daily_goal = %s WHERE id = %s',
            (new_goal_int, user_id)
        )

        if result:
            return jsonify({'success': True, 'message': 'Goal updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update goal'})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to update goal: {str(e)}'})

@app.route('/update_theme', methods=['POST'])
@login_required
def update_theme():
    theme = request.json.get('theme')
    user_id = session['user_id']

    result = db.execute_query(
        'UPDATE users SET theme = %s WHERE id = %s',
        (theme, user_id)
    )

    if result:
        session['theme'] = theme
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update theme'})

@app.route('/update_email_settings', methods=['POST'])
@login_required
def update_email_settings():
    email_notifications = request.json.get('email_notifications', 0)
    reminder_frequency = request.json.get('reminder_frequency', 'daily')
    user_id = session['user_id']

    result = db.execute_query(
        'UPDATE users SET email_notifications = %s, reminder_frequency = %s WHERE id = %s',
        (email_notifications, reminder_frequency, user_id)
    )

    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update email settings'})

# ===== SMARTWATCH API ROUTES =====
@app.route('/api/watch/status')
@login_required
def watch_status():
    """Simple status for smartwatch"""
    user_id = session['user_id']

    today_str = date.today().isoformat()
    today_intake = db.execute_one('''
        SELECT SUM(amount) as total FROM water_intake 
        WHERE user_id = %s AND DATE(timestamp) = DATE(%s)
    ''', (user_id, today_str))

    user = db.execute_one('SELECT daily_goal FROM users WHERE id = %s', (user_id,))

    total_today = today_intake['total'] or 0 if today_intake else 0
    daily_goal = user['daily_goal'] or 2000 if user else 2000

    return jsonify({
        'current': total_today,
        'goal': daily_goal,
        'percent': min((total_today / daily_goal) * 100, 100),
        'message': f'{total_today}ml / {daily_goal}ml'
    })

@app.route('/api/watch/log', methods=['POST'])
@login_required
def watch_log():
    """Simple log from smartwatch"""
    try:
        user_id = session['user_id']
        amount = request.json.get('amount', 250)

        # Convert to integer first
        try:
            amount_int = int(amount)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Amount must be a valid number'})

        if amount_int <= 0:
            return jsonify({'success': False, 'error': 'Invalid amount'})

        result = db.execute_query(
            'INSERT INTO water_intake (user_id, amount) VALUES (%s, %s)',
            (user_id, amount_int)
        )

        if not result:
            return jsonify({'success': False, 'error': 'Failed to log water'})

        today_str = date.today().isoformat()
        today_intake = db.execute_one('''
            SELECT SUM(amount) as total FROM water_intake 
            WHERE user_id = %s AND DATE(timestamp) = DATE(%s)
        ''', (user_id, today_str))

        total_today = today_intake['total'] or 0 if today_intake else 0

        return jsonify({
            'success': True,
            'message': f'Logged {amount_int}ml',
            'total_today': total_today
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to log water: {str(e)}'})

@app.route('/api/watch/quick/<int:amount>')
@login_required
def watch_quick_log(amount):
    """Ultra-simple logging via URL - for watch browser"""
    user_id = session['user_id']

    if amount <= 0:
        return "Invalid amount"

    result = db.execute_query(
        'INSERT INTO water_intake (user_id, amount) VALUES (%s, %s)',
        (user_id, amount)
    )

    if not result:
        return "Failed to log water"

    return f"""
    <html>
    <head>
        <title>Water Logged</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                text-align: center; 
                padding: 2rem;
                margin: 0;
            }}
            .container {{ 
                background: rgba(255,255,255,0.1); 
                padding: 2rem; 
                border-radius: 20px; 
                backdrop-filter: blur(10px);
            }}
            .success {{ font-size: 3rem; margin: 1rem 0; }}
            .message {{ font-size: 1.5rem; margin: 1rem 0; }}
            .button {{ 
                display: inline-block; 
                background: white; 
                color: #667eea; 
                padding: 1rem 2rem; 
                border-radius: 10px; 
                text-decoration: none; 
                margin: 0.5rem;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">✅</div>
            <div class="message">Logged {amount}ml successfully!</div>
            <div>
                <a href="/watch" class="button">Back to Watch</a>
                <a href="/dashboard" class="button">Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/watch/history')
@login_required
def watch_history():
    """Get recent history for smartwatch"""
    user_id = session['user_id']

    recent = db.execute_query('''
        SELECT amount, timestamp 
        FROM water_intake 
        WHERE user_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''', (user_id,), fetch=True)

    logs = []
    if recent:
        for log in recent:
            timestamp_str = log['timestamp'].strftime('%H:%M') if hasattr(log['timestamp'], 'strftime') else str(log['timestamp'])[11:16]
            logs.append({
                'amount': log['amount'],
                'time': timestamp_str
            })

    return jsonify({'recent_logs': logs})

@app.route('/watch')
@login_required
def watch_setup():
    """Smartwatch setup page"""
    return render_template('watch_setup.html')

# ===== HELPER FUNCTIONS =====
def check_achievements(user_id):
    conn = db.get_connection()
    if not conn:
        return

    try:
        # Check first log achievement
        first_log = db.execute_one('''
            SELECT COUNT(*) as count FROM water_intake WHERE user_id = %s
        ''', (user_id,))

        if first_log and first_log['count'] == 1:
            unlock_achievement(user_id, 1)

        # Check overachiever achievement
        max_daily = db.execute_one('''
            SELECT SUM(amount) as total FROM water_intake 
            WHERE user_id = %s 
            GROUP BY DATE(timestamp) 
            ORDER BY total DESC LIMIT 1
        ''', (user_id,))

        if max_daily and max_daily['total'] >= 3000:
            unlock_achievement(user_id, 4)

        # Check streak achievements
        current_streak = calculate_streak(user_id)
        if current_streak >= 3:
            unlock_achievement(user_id, 2)
        if current_streak >= 7:
            unlock_achievement(user_id, 3)

    except Exception as e:
        print(f"Error checking achievements: {e}")

def unlock_achievement(user_id, achievement_id):
    try:
        # Check if already unlocked
        existing = db.execute_one('''
            SELECT 1 FROM user_achievements WHERE user_id = %s AND achievement_id = %s
        ''', (user_id, achievement_id))

        if not existing:
            result = db.execute_query(
                'INSERT INTO user_achievements (user_id, achievement_id) VALUES (%s, %s)',
                (user_id, achievement_id)
            )

            if result:
                # Send achievement email
                achievement = db.execute_one(
                    'SELECT * FROM achievements WHERE id = %s', (achievement_id,)
                )

                if achievement:
                    print(f"🎉 Achievement unlocked: {achievement['name']} for user {user_id}")
                    threading.Thread(
                        target=email_service.send_achievement_unlocked,
                        args=(user_id, achievement)
                    ).start()

    except Exception as e:
        print(f"❌ Error unlocking achievement: {e}")

def calculate_streak(user_id):
    dates = db.execute_query('''
        SELECT DATE(timestamp) as date, SUM(amount) as total 
        FROM water_intake 
        WHERE user_id = %s 
        GROUP BY DATE(timestamp) 
        ORDER BY date DESC
    ''', (user_id,), fetch=True)

    streak = 0
    today = date.today()

    if dates:
        for i, day_data in enumerate(dates):
            try:
                if isinstance(day_data['date'], str):
                    day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                else:
                    day_date = day_data['date']
            except (ValueError, TypeError):
                continue

            expected_date = today - timedelta(days=i)

            if day_date == expected_date and day_data['total'] >= 2000:
                streak += 1
            else:
                break

    return streak

def get_weather_based_recommendation():
    try:
        base_goal = 2000
        base_goal += 300  # Simulate hot weather
        return base_goal
    except:
        return 2300

# Stop scheduler when app exits
atexit.register(lambda: email_scheduler.stop())

if __name__ == '__main__':
    print("🚀 Starting HydroTracker Flask application...")
    print("📧 Test email routes:")
    print("   - /test-email-simple (no login required)")
    app.run(debug=True)