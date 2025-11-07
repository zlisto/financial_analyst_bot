"""
Bitcoin Analyzer Scheduler
Runs the analysis and sends email immediately, then schedules daily at 8 AM
"""

import os
import sys
import time
import schedule
from datetime import datetime

# Fix Windows console encoding issues (only if not already wrapped)
if sys.platform == 'win32' and not isinstance(sys.stdout, type(sys.__stdout__)):
    try:
        import io
        if not hasattr(sys.stdout, 'buffer') or sys.stdout.buffer.closed:
            pass  # Already handled or closed
        else:
            if not isinstance(sys.stdout, io.TextIOWrapper):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            if not isinstance(sys.stderr, io.TextIOWrapper):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass  # Ignore if already wrapped or closed

from run_and_email import main as run_analysis_and_email

def job():
    """Job function to run analysis and send email"""
    print("\n" + "="*80)
    print(f"Scheduled job started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    try:
        run_analysis_and_email()
        print(f"Job completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Error in scheduled job: {str(e)}")
        import traceback
        traceback.print_exc()
    print("="*80 + "\n")

def main():
    """Main scheduler function"""
    print("="*80)
    print("BITCOIN ANALYSIS EMAIL SCHEDULER")
    print("="*80)
    print()
    print("This script will:")
    print("1. Run the analysis and send email immediately")
    print("2. Schedule daily runs at 8:00 AM")
    print("3. Run forever (press Ctrl+C to stop)")
    print()
    print("="*80)
    print()
    
    # Schedule daily at 8 AM
    schedule.every().day.at("08:00").do(job)
    print("Scheduled daily runs at 8:00 AM")
    print()
    
    # Run immediately
    print("Running initial analysis now...")
    print("-" * 80)
    job()
    
    # Keep running and check schedule
    print("Scheduler is now running. Waiting for next scheduled run...")
    print("Next run scheduled for: 8:00 AM daily")
    print("Press Ctrl+C to stop the scheduler")
    print()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n" + "="*80)
        print("Scheduler stopped by user")
        print("="*80)

if __name__ == "__main__":
    main()

