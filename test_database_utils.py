# simple_test_dashboard.py
# Simple test with your specific user ID

from database_utils import get_dashboard_stats
import json

def test_with_your_user_id():
    # Your specific user ID
    user_id = "48ec6da1-cb94-4632-9c2f-5563aa2133f8"
    
    print(f"Testing dashboard stats with user_id: {user_id}")
    print("="*60)
    
    try:
        result = get_dashboard_stats(user_id)
        
        if result is None:
            print("❌ Function returned None")
            return
        
        print("✅ SUCCESS! Function executed without errors")
        print("\n" + "="*60)
        print("COMPLETE RESULT:")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))
        
        print("\n" + "="*60)
        print("SUMMARY:")
        print("="*60)
        
        # Current user summary
        if 'current_user' in result:
            cu = result['current_user']
            print(f"YOUR STATS:")
            print(f"  All-time sessions: {cu.get('total_sessions_all_time', 0)}")
            print(f"  This year sessions: {cu.get('total_sessions_this_year', 0)}")
            print(f"  Sessions/week: {cu.get('sessions_per_week_this_year', 0)}")
            print(f"  Avg rating: {cu.get('avg_fun_rating_this_year', 'N/A')}")
        
        # Other users summary
        if 'other_users' in result:
            others = result['other_users']
            print(f"\nOTHER USERS: {len(others)} found")
            for user in others[:3]:  # Show first 3
                print(f"  {user.get('display_name', 'Unknown')}: {user.get('total_sessions_all_time', 0)} sessions")
        
        # Community summary
        if 'community' in result:
            comm = result['community']
            print(f"\nCOMMUNITY:")
            print(f"  Total sessions: {comm.get('total_sessions', 0)}")
            print(f"  Total stoke: {comm.get('total_stoke', 0)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_your_user_id()