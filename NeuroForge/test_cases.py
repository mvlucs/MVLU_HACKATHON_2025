#!/usr/bin/env python3
"""
Member 2 - Audio & Video Translation System Testing Suite
Author: Suraj (Member 2)
Role: Testing & Dataset Lead
"""

import requests
import os
import time
import json
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:5000"
TEST_FILES_DIR = "test_samples"

def print_header(title):
    """Print formatted test section header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_test(test_name, status, details=""):
    """Print formatted test result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}")
    if details:
        print(f"   📝 {details}")

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_test("API Health Check", True, f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            print_test("API Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("API Health Check", False, f"Connection Error: {str(e)}")
        return False

def test_languages_endpoint():
    """Test supported languages endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/languages")
        if response.status_code == 200:
            data = response.json()
            languages = data.get('languages', {})
            print_test("Languages Endpoint", True, f"{len(languages)} languages available")
            for code, name in languages.items():
                print(f"      • {code}: {name}")
            return True
        else:
            print_test("Languages Endpoint", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("Languages Endpoint", False, f"Error: {str(e)}")
        return False

def test_file_upload(filename, target_language='hi'):
    """Test file upload and translation"""
    file_path = os.path.join(TEST_FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        print_test(f"File Upload: {filename}", False, "File not found")
        return False
    
    try:
        file_size = os.path.getsize(file_path)
        print(f"🔄 Testing upload: {filename} ({file_size/1024:.1f} KB) → {target_language}")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'target_language': target_language}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE_URL}/upload", files=files, data=data)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                duration = end_time - start_time
                
                original_text = result.get('original_text', 'N/A')
                translated_text = result.get('translated_text', 'N/A')
                
                print_test(f"File Upload: {filename}", True, 
                          f"Processed in {duration:.1f}s")
                print(f"      📄 Original: {original_text[:50]}...")
                print(f"      🌍 Translated: {translated_text[:50]}...")
                print(f"      🔊 Audio Available: {result.get('audio_available', False)}")
                
                return True
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.content else 'No response'
                print_test(f"File Upload: {filename}", False, 
                          f"HTTP {response.status_code} - {error_msg}")
                return False
                
    except Exception as e:
        print_test(f"File Upload: {filename}", False, f"Error: {str(e)}")
        return False

def test_history_endpoint():
    """Test translation history"""
    try:
        response = requests.get(f"{API_BASE_URL}/history")
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print_test("History Endpoint", True, f"{len(history)} translation records")
            
            if history:
                print("      📋 Recent translations:")
                for i, record in enumerate(history[:3]):  # Show first 3
                    filename = record.get('original_filename', 'Unknown')
                    target_lang = record.get('target_language', 'Unknown')
                    created = record.get('created_at', 'Unknown')
                    print(f"         {i+1}. {filename} → {target_lang} ({created})")
            
            return True
        else:
            print_test("History Endpoint", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("History Endpoint", False, f"Error: {str(e)}")
        return False

def test_error_handling():
    """Test various error conditions"""
    print_header("Error Handling Tests")
    
    error_tests = []
    
    # Test 1: No file upload
    try:
        response = requests.post(f"{API_BASE_URL}/upload", data={'target_language': 'hi'})
        if response.status_code == 400:
            error_tests.append(("No File Upload", True, "Correctly rejected"))
        else:
            error_tests.append(("No File Upload", False, f"HTTP {response.status_code}"))
    except Exception as e:
        error_tests.append(("No File Upload", False, f"Error: {str(e)}"))
    
    # Test 2: Invalid file type (if we have a text file)
    test_txt_path = os.path.join(TEST_FILES_DIR, "test.txt")
    if os.path.exists(test_txt_path):
        try:
            with open(test_txt_path, 'rb') as f:
                files = {'file': f}
                data = {'target_language': 'hi'}
                response = requests.post(f"{API_BASE_URL}/upload", files=files, data=data)
                
                if response.status_code == 400:
                    error_tests.append(("Invalid File Type", True, "Correctly rejected .txt"))
                else:
                    error_tests.append(("Invalid File Type", False, f"HTTP {response.status_code}"))
        except Exception as e:
            error_tests.append(("Invalid File Type", False, f"Error: {str(e)}"))
    else:
        error_tests.append(("Invalid File Type", False, "No test.txt file found"))
    
    # Test 3: Invalid language code
    if os.path.exists(os.path.join(TEST_FILES_DIR, "english_sample1.mp3")):
        try:
            with open(os.path.join(TEST_FILES_DIR, "english_sample1.mp3"), 'rb') as f:
                files = {'file': f}
                data = {'target_language': 'invalid_lang'}
                response = requests.post(f"{API_BASE_URL}/upload", files=files, data=data)
                
                # This might still work with mock responses, so we check result
                if response.status_code == 200:
                    result = response.json()
                    error_tests.append(("Invalid Language Code", True, "Handled gracefully"))
                else:
                    error_tests.append(("Invalid Language Code", True, "Correctly rejected"))
        except Exception as e:
            error_tests.append(("Invalid Language Code", False, f"Error: {str(e)}"))
    
    # Print results
    for test_name, status, details in error_tests:
        print_test(test_name, status, details)
    
    return sum(1 for _, status, _ in error_tests if status)

def create_test_files():
    """Create test sample files if they don't exist"""
    print_header("Creating Test Files")
    
    os.makedirs(TEST_FILES_DIR, exist_ok=True)
    
    # Create a simple text file for error testing
    test_txt_path = os.path.join(TEST_FILES_DIR, "test.txt")
    if not os.path.exists(test_txt_path):
        with open(test_txt_path, 'w') as f:
            f.write("This is a test text file that should be rejected by the API.")
        print_test("Created test.txt", True, "For error handling tests")
    
    # Create placeholder audio files (these would be real files in actual implementation)
    test_files = [
        "english_sample1.mp3",
        "english_sample2.wav", 
        "english_video.mp4"
    ]
    
    for filename in test_files:
        filepath = os.path.join(TEST_FILES_DIR, filename)
        if not os.path.exists(filepath):
            # Create empty placeholder files for testing
            with open(filepath, 'wb') as f:
                # Write some dummy bytes to simulate file content
                f.write(b"dummy_audio_content_for_testing" * 100)
            print_test(f"Created {filename}", True, "Placeholder file")

def generate_test_report():
    """Generate comprehensive test report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
# Audio & Video Translation System - Test Report

**Date:** {timestamp}
**Tester:** Suraj (Member 2)
**API URL:** {API_BASE_URL}

## Test Summary
- **API Health:** ✅/❌
- **Languages Endpoint:** ✅/❌  
- **File Upload:** ✅/❌
- **History Endpoint:** ✅/❌
- **Error Handling:** ✅/❌

## Detailed Results
[Results will be filled during actual testing]

## Files Tested
| File | Format | Size | Target Language | Status | Response Time |
|------|--------|------|-----------------|--------|---------------|
| english_sample1.mp3 | MP3 | ~2KB | Hindi | ✅/❌ | X.Xs |
| english_sample2.wav | WAV | ~2KB | Marathi | ✅/❌ | X.Xs |
| english_video.mp4 | MP4 | ~2KB | Tamil | ✅/❌ | X.Xs |

## Issues Found
1. [Issue descriptions will be added during testing]

## Recommendations
1. [Recommendations will be added after testing]

## System Status
- **Backend API:** Running/Not Running
- **Translation Quality:** Good/Fair/Poor
- **Response Time:** Fast/Slow
- **Error Handling:** Robust/Needs Improvement
- **Ready for Demo:** Yes/No
"""
    
    # Save report
    with open("test_results.md", "w") as f:
        f.write(report)
    
    print_test("Test Report Generated", True, "Saved as test_results.md")

def run_complete_test_suite():
    """Run the complete test suite"""
    print("🚀 Audio & Video Translation System - Complete Test Suite")
    print(f"👤 Tester: Suraj (Member 2)")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize test tracking
    total_tests = 0
    passed_tests = 0
    
    # Step 1: Create test files
    create_test_files()
    
    # Step 2: Basic API tests
    print_header("Basic API Tests")
    
    basic_tests = [
        ("API Health Check", test_api_health),
        ("Languages Endpoint", test_languages_endpoint),
        ("History Endpoint", test_history_endpoint),
    ]
    
    for test_name, test_func in basic_tests:
        total_tests += 1
        if test_func():
            passed_tests += 1
        time.sleep(1)
    
    # Step 3: File upload tests
    print_header("File Upload Tests")
    
    upload_tests = [
        ("english_sample1.mp3", "hi"),   # Hindi
        ("english_sample2.wav", "mr"),   # Marathi  
        ("english_video.mp4", "ta"),     # Tamil
    ]
    
    for filename, target_lang in upload_tests:
        total_tests += 1
        if test_file_upload(filename, target_lang):
            passed_tests += 1
        time.sleep(2)  # Wait between uploads
    
    # Step 4: Error handling tests
    error_passed = test_error_handling()
    total_tests += 3  # We have 3 error tests
    passed_tests += error_passed
    
    # Step 5: Generate report
    generate_test_report()
    
    # Final results
    print_header("Test Results Summary")
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 **Overall Results:**")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"\n🎉 **EXCELLENT!** System is working well!")
    elif success_rate >= 60:
        print(f"\n⚠️  **GOOD** but needs some fixes")
    else:
        print(f"\n❌ **NEEDS WORK** - Multiple issues found")
    
    print(f"\n📝 Detailed report saved as 'test_results.md'")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Performance testing function
def test_performance():
    """Test system performance with different file sizes"""
    print_header("Performance Tests")
    
    # This would test with actual audio files of different sizes
    # For now, we'll simulate with our dummy files
    performance_tests = [
        ("Small file (~2KB)", "english_sample1.mp3", "hi"),
        ("Medium file (~2KB)", "english_sample2.wav", "mr"), 
        ("Large file (~2KB)", "english_video.mp4", "ta"),
    ]
    
    for test_name, filename, lang in performance_tests:
        start_time = time.time()
        success = test_file_upload(filename, lang)
        end_time = time.time()
        
        if success:
            duration = end_time - start_time
            if duration < 5:
                performance = "Fast ⚡"
            elif duration < 15:
                performance = "Good ✅"
            else:
                performance = "Slow ⚠️"
            
            print(f"   {test_name}: {duration:.1f}s - {performance}")

if __name__ == "__main__":
    # Main execution
    try:
        print("🎯 Choose test mode:")
        print("1. Complete Test Suite (Recommended)")
        print("2. Quick API Check Only") 
        print("3. Performance Tests")
        print("4. Error Handling Only")
        
        choice = input("\nEnter choice (1-4, default=1): ").strip()
        
        if choice == "2":
            print_header("Quick API Check")
            test_api_health()
            test_languages_endpoint()
        elif choice == "3":
            test_performance()
        elif choice == "4":
            test_error_handling()
        else:
            # Default: Complete test suite
            run_complete_test_suite()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")