# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from database import get_db_connection
# from flask import current_app
#
#
# class EmailService:
#     def __init__(self):
#         self.mail_config = {
#             'server': 'smtp.gmail.com',
#             'port': 587,
#             'username': 'ashkolhe65@gmail.com',
#             'password': 'wtlj mlsg copa iynv',
#             'use_tls': True
#         }
#
#     def _send_email(self, to_email, subject, html_content):
#         """Send email using SMTP"""
#         try:
#             print(f"📧 Attempting to send email to: {to_email}")
#
#             # Create message
#             msg = MIMEMultipart()
#             msg['From'] = self.mail_config['username']
#             msg['To'] = to_email
#             msg['Subject'] = subject
#
#             # Add HTML content
#             msg.attach(MIMEText(html_content, 'html'))
#
#             # Create SMTP session
#             server = smtplib.SMTP(self.mail_config['server'], self.mail_config['port'])
#             server.ehlo()
#
#             if self.mail_config['use_tls']:
#                 server.starttls()
#                 server.ehlo()
#
#             # Login and send email
#             server.login(self.mail_config['username'], self.mail_config['password'])
#             text = msg.as_string()
#             server.sendmail(self.mail_config['username'], to_email, text)
#             server.quit()
#
#             print(f"✅ Email sent successfully to: {to_email}")
#             return True
#
#         except Exception as e:
#             print(f"❌ Failed to send email to {to_email}: {str(e)}")
#             return False
#
#     def get_user_email(self, user_id):
#         """Get user email from database"""
#         conn = get_db_connection()
#         user = conn.execute('SELECT email, username FROM users WHERE id = ?', (user_id,)).fetchone()
#         conn.close()
#         return user
#
#     def send_daily_reminder(self, user_id):
#         """Send daily water reminder"""
#         user = self.get_user_email(user_id)
#         if not user:
#             return False
#
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
#                 .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
#                 .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
#                 .content {{ padding: 20px; }}
#                 .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
#                 .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>💧 HydroTracker Reminder</h1>
#                 </div>
#                 <div class="content">
#                     <h2>Hello {user['username']}!</h2>
#                     <p>This is your friendly reminder to stay hydrated! 💦</p>
#                     <p>Remember to drink water regularly throughout the day to maintain your health and energy levels.</p>
#                     <p><strong>Recommended:</strong> Drink at least 8 glasses (2 liters) of water today!</p>
#                     <br>
#                     <center>
#                         <a href="http://localhost:5000" class="button">Log Your Water Intake</a>
#                     </center>
#                 </div>
#                 <div class="footer">
#                     <p>This email was sent from HydroTracker App</p>
#                     <p>You can manage your email preferences in your account settings.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
#
#         return self._send_email(user['email'], '💧 Time to Hydrate! - HydroTracker', html_content)
#
#     def send_goal_reminder(self, user_id):
#         """Send goal progress reminder"""
#         user = self.get_user_email(user_id)
#         if not user:
#             return False
#
#         # Get today's progress
#         conn = get_db_connection()
#         today_intake = conn.execute('''
#             SELECT SUM(amount) as total FROM water_intake
#             WHERE user_id = ? AND DATE(timestamp) = DATE('now')
#         ''', (user_id,)).fetchone()
#
#         user_goal = conn.execute('SELECT daily_goal FROM users WHERE id = ?', (user_id,)).fetchone()
#         conn.close()
#
#         total_today = today_intake['total'] or 0
#         daily_goal = user_goal['daily_goal'] or 2000
#         progress = min((total_today / daily_goal) * 100, 100)
#
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
#                 .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
#                 .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
#                 .content {{ padding: 20px; }}
#                 .progress {{ background: #f0f0f0; border-radius: 10px; height: 20px; margin: 20px 0; }}
#                 .progress-bar {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; border-radius: 10px; width: {progress}%; }}
#                 .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
#                 .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>📊 Daily Goal Update</h1>
#                 </div>
#                 <div class="content">
#                     <h2>Hello {user['username']}!</h2>
#                     <p>Here's your daily water intake progress:</p>
#
#                     <div class="stats">
#                         <h3>Today's Progress: {progress:.1f}%</h3>
#                         <div class="progress">
#                             <div class="progress-bar"></div>
#                         </div>
#                         <p><strong>{total_today}ml</strong> / <strong>{daily_goal}ml</strong></p>
#                     </div>
#
#                     <p>{"🎉 Great job! You've met your daily goal!" if progress >= 100 else "💪 Keep going! You're making good progress!"}</p>
#
#                     <center>
#                         <a href="http://localhost:5000" class="button">Add More Water</a>
#                     </center>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
#
#         return self._send_email(user['email'], '📊 Your Daily Water Goal - HydroTracker', html_content)
#
#     def send_achievement_unlocked(self, user_id, achievement):
#         """Send achievement unlocked email"""
#         user = self.get_user_email(user_id)
#         if not user:
#             return False
#
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
#                 .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
#                 .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
#                 .achievement {{ text-align: center; padding: 20px; }}
#                 .icon {{ font-size: 4rem; margin: 20px 0; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>🎉 Achievement Unlocked!</h1>
#                 </div>
#                 <div class="achievement">
#                     <div class="icon">{achievement['icon']}</div>
#                     <h2>{achievement['name']}</h2>
#                     <p>{achievement['description']}</p>
#                     <p><em>Keep up the great work in staying hydrated!</em></p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
#
#         return self._send_email(user['email'], f"🎉 Achievement Unlocked: {achievement['name']} - HydroTracker",
#                                 html_content)
#
#     def send_welcome_email(self, user_id):
#         """Send welcome email to new users"""
#         user = self.get_user_email(user_id)
#         if not user:
#             return False
#
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
#                 .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
#                 .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
#                 .content {{ padding: 20px; }}
#                 .feature {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
#                 .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>🚀 Welcome to HydroTracker!</h1>
#                 </div>
#                 <div class="content">
#                     <h2>Hello {user['username']}!</h2>
#                     <p>Welcome to HydroTracker - your personal hydration companion! We're excited to help you stay hydrated and healthy.</p>
#
#                     <div class="feature">
#                         <h3>💧 Track Your Water Intake</h3>
#                         <p>Log your daily water consumption and monitor your progress.</p>
#                     </div>
#
#                     <div class="feature">
#                         <h3>🎯 Set Daily Goals</h3>
#                         <p>Customize your daily water intake goals based on your needs.</p>
#                     </div>
#
#                     <div class="feature">
#                         <h3>📊 View Analytics</h3>
#                         <p>Get insights into your hydration patterns and progress.</p>
#                     </div>
#
#                     <div class="feature">
#                         <h3>🏆 Earn Achievements</h3>
#                         <p>Unlock achievements as you build healthy hydration habits.</p>
#                     </div>
#
#                     <center>
#                         <a href="http://localhost:5000/dashboard" class="button">Get Started</a>
#                     </center>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
#
#         return self._send_email(user['email'], '🚀 Welcome to HydroTracker!', html_content)
#
#
# # Create global instance
# email_service = EmailService()





import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import db
from flask import current_app


class EmailService:
    def __init__(self):
        self.mail_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'syedamahwish06@gmail.com',
            'password': 'ljqb ycvm udbn namf',
            'use_tls': True
        }

    def _send_email(self, to_email, subject, html_content):
        """Send email using SMTP"""
        try:
            print(f"📧 Attempting to send email to: {to_email}")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.mail_config['username']
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Create SMTP session
            server = smtplib.SMTP(self.mail_config['server'], self.mail_config['port'])
            server.ehlo()

            if self.mail_config['use_tls']:
                server.starttls()
                server.ehlo()

            # Login and send email
            server.login(self.mail_config['username'], self.mail_config['password'])
            text = msg.as_string()
            server.sendmail(self.mail_config['username'], to_email, text)
            server.quit()

            print(f"✅ Email sent successfully to: {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False

    def get_user_email(self, user_id):
        """Get user email from database"""
        return db.execute_one('SELECT email, username FROM users WHERE id = %s', (user_id,))

    def send_daily_reminder(self, user_id):
        """Send daily water reminder"""
        user = self.get_user_email(user_id)
        if not user:
            return False

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💧 HydroTracker Reminder</h1>
                </div>
                <div class="content">
                    <h2>Hello {user['username']}!</h2>
                    <p>This is your friendly reminder to stay hydrated! 💦</p>
                    <p>Remember to drink water regularly throughout the day to maintain your health and energy levels.</p>
                    <p><strong>Recommended:</strong> Drink at least 8 glasses (2 liters) of water today!</p>
                    <br>
                    <center>
                        <a href="http://localhost:5000" class="button">Log Your Water Intake</a>
                    </center>
                </div>
                <div class="footer">
                    <p>This email was sent from HydroTracker App</p>
                    <p>You can manage your email preferences in your account settings.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self._send_email(user['email'], '💧 Time to Hydrate! - HydroTracker', html_content)

    def send_goal_reminder(self, user_id):
        """Send goal progress reminder"""
        user = self.get_user_email(user_id)
        if not user:
            return False

        # Get today's progress
        today_intake = db.execute_one('''
            SELECT SUM(amount) as total FROM water_intake 
            WHERE user_id = %s AND DATE(timestamp) = CURDATE()
        ''', (user_id,))

        user_goal = db.execute_one('SELECT daily_goal FROM users WHERE id = %s', (user_id,))

        total_today = today_intake['total'] or 0 if today_intake else 0
        daily_goal = user_goal['daily_goal'] or 2000 if user_goal else 2000
        progress = min((total_today / daily_goal) * 100, 100) if daily_goal > 0 else 0

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .progress {{ background: #f0f0f0; border-radius: 10px; height: 20px; margin: 20px 0; }}
                .progress-bar {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; border-radius: 10px; width: {progress}%; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Goal Update</h1>
                </div>
                <div class="content">
                    <h2>Hello {user['username']}!</h2>
                    <p>Here's your daily water intake progress:</p>

                    <div class="stats">
                        <h3>Today's Progress: {progress:.1f}%</h3>
                        <div class="progress">
                            <div class="progress-bar"></div>
                        </div>
                        <p><strong>{total_today}ml</strong> / <strong>{daily_goal}ml</strong></p>
                    </div>

                    <p>{"🎉 Great job! You've met your daily goal!" if progress >= 100 else "💪 Keep going! You're making good progress!"}</p>

                    <center>
                        <a href="http://localhost:5000" class="button">Add More Water</a>
                    </center>
                </div>
            </div>
        </body>
        </html>
        """

        return self._send_email(user['email'], '📊 Your Daily Water Goal - HydroTracker', html_content)

    def send_achievement_unlocked(self, user_id, achievement):
        """Send achievement unlocked email"""
        user = self.get_user_email(user_id)
        if not user:
            return False

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .achievement {{ text-align: center; padding: 20px; }}
                .icon {{ font-size: 4rem; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Achievement Unlocked!</h1>
                </div>
                <div class="achievement">
                    <div class="icon">{achievement['icon']}</div>
                    <h2>{achievement['name']}</h2>
                    <p>{achievement['description']}</p>
                    <p><em>Keep up the great work in staying hydrated!</em></p>
                </div>
            </div>
        </body>
        </html>
        """

        return self._send_email(user['email'], f"🎉 Achievement Unlocked: {achievement['name']} - HydroTracker",
                                html_content)

    def send_welcome_email(self, user_id):
        """Send welcome email to new users"""
        user = self.get_user_email(user_id)
        if not user:
            return False

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .feature {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .button {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Welcome to HydroTracker!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user['username']}!</h2>
                    <p>Welcome to HydroTracker - your personal hydration companion! We're excited to help you stay hydrated and healthy.</p>

                    <div class="feature">
                        <h3>💧 Track Your Water Intake</h3>
                        <p>Log your daily water consumption and monitor your progress.</p>
                    </div>

                    <div class="feature">
                        <h3>🎯 Set Daily Goals</h3>
                        <p>Customize your daily water intake goals based on your needs.</p>
                    </div>

                    <div class="feature">
                        <h3>📊 View Analytics</h3>
                        <p>Get insights into your hydration patterns and progress.</p>
                    </div>

                    <div class="feature">
                        <h3>🏆 Earn Achievements</h3>
                        <p>Unlock achievements as you build healthy hydration habits.</p>
                    </div>

                    <center>
                        <a href="http://localhost:5000/dashboard" class="button">Get Started</a>
                    </center>
                </div>
            </div>
        </body>
        </html>
        """

        return self._send_email(user['email'], '🚀 Welcome to HydroTracker!', html_content)


# Create global instance
email_service = EmailService()