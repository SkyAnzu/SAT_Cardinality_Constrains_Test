#!/usr/bin/env python3
"""
CSV Result Analyzer for CBP Test Results
Analyze and generate reports from CSV test result files
"""

import pandas as pd
import sys
import os
import glob
from datetime import datetime

# Optional imports for plotting
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

def find_latest_csv():
    """Find the latest CSV result file"""
    csv_files = glob.glob("cbp_test_results_*.csv")
    if not csv_files:
        csv_files = glob.glob("results/cbp_test_results_*.csv")
    
    if not csv_files:
        return None
    
    return max(csv_files, key=os.path.getctime)

def analyze_results(csv_file):
    """Analyze results from CSV file"""
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return
    
    # Check empty DataFrame
    if df.empty:
        print("❌ CSV file is empty!")
        return
    
    # Check required columns
    required_columns = ['file_name', 'solver', 'success']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return
    
    # Handle missing values
    df['success'] = df['success'].fillna(False)
    df['timeout'] = df['timeout'].fillna(False) if 'timeout' in df.columns else False
    
    print(f"📊 Analyzing results from: {csv_file}")
    print(f"📈 Total tests: {len(df)}")
    print("=" * 60)
    
    # 1. Overview
    print("\n1. OVERVIEW:")
    print(f"   - Number of test files: {df['file_name'].nunique()}")
    print(f"   - Number of solvers: {df['solver'].nunique()}")
    success_count = df['success'].sum()
    success_rate = df['success'].mean() * 100 if len(df) > 0 else 0
    print(f"   - Successful tests: {success_count}/{len(df)} ({success_rate:.1f}%)")
    
    if 'timeout' in df.columns:
        timeout_count = df['timeout'].sum()
        timeout_rate = df['timeout'].mean() * 100 if len(df) > 0 else 0
        print(f"   - Timeout tests: {timeout_count}/{len(df)} ({timeout_rate:.1f}%)")
    
    # 2. Statistics by solver
    print("\n2. STATISTICS BY SOLVER:")
    try:
        # Only aggregate existing columns
        agg_dict = {'success': ['count', 'sum', 'mean']}
        if 'runtime_sec' in df.columns:
            agg_dict['runtime_sec'] = ['mean', 'max']
        if 'bandwidth' in df.columns:
            agg_dict['bandwidth'] = 'mean'
        if 'timeout' in df.columns:
            agg_dict['timeout'] = 'sum'
            
        solver_stats = df.groupby('solver').agg(agg_dict).round(2)
        print(solver_stats)
    except Exception as e:
        print(f"   Error calculating solver statistics: {e}")
    
    # 3. Statistics by graph size
    print("\n3. STATISTICS BY GRAPH SIZE:")
    df_success = df[df['success'] == True]
    if not df_success.empty and 'vertices' in df_success.columns and 'edges' in df_success.columns:
        try:
            agg_dict = {}
            if 'bandwidth' in df_success.columns:
                agg_dict['bandwidth'] = ['mean', 'min', 'max']
            if 'runtime_sec' in df_success.columns:
                agg_dict['runtime_sec'] = ['mean', 'min', 'max']
                
            if agg_dict:
                size_stats = df_success.groupby(['vertices', 'edges']).agg(agg_dict).round(2)
                print(size_stats.head(10))
            else:
                print("   No suitable data")
        except Exception as e:
            print(f"   Error calculating size statistics: {e}")
    else:
        print("   No successful data or missing vertices/edges columns")
    
    # 4. Top 10 fastest tests
    print("\n4. TOP 10 FASTEST TESTS:")
    if not df_success.empty and 'runtime_sec' in df_success.columns:
        try:
            display_cols = ['file_name', 'solver']
            if 'bandwidth' in df_success.columns:
                display_cols.append('bandwidth')
            display_cols.append('runtime_sec')
            
            fastest = df_success.nsmallest(10, 'runtime_sec')[display_cols]
            print(fastest.to_string(index=False))
        except Exception as e:
            print(f"   Error finding fastest tests: {e}")
    else:
        print("   No runtime data")
    
    # 5. Problematic tests
    print("\n5. PROBLEMATIC TESTS:")
    failed = df[df['success'] == False]
    if not failed.empty:
        print(f"   Number of failed tests: {len(failed)}")
        for _, row in failed.iterrows():
            error_msg = row.get('error_msg', 'No error information')
            if pd.isna(error_msg) or error_msg is None:
                error_msg = "No error information"
            error_preview = str(error_msg)[:50] + "..." if len(str(error_msg)) > 50 else str(error_msg)
            print(f"   - {row['file_name']} ({row['solver']}): {error_preview}")
    else:
        print("   ✅ No failed tests!")
    
    # 6. Create detailed report
    create_detailed_report(df, csv_file)

def create_detailed_report(df, csv_file):
    """Create detailed report and charts"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"cbp_analysis_report_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("CYCLIC BANDWIDTH PROBLEM - ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Data file: {csv_file}\n")
            f.write(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overall statistics
            f.write("1. OVERALL STATISTICS:\n")
            f.write(f"   - Total tests: {len(df)}\n")
            f.write(f"   - Number of test files: {df['file_name'].nunique()}\n")
            f.write(f"   - Number of solvers: {df['solver'].nunique()}\n")
            
            success_count = df['success'].sum()
            success_rate = df['success'].mean() * 100 if len(df) > 0 else 0
            f.write(f"   - Successful tests: {success_count}/{len(df)} ({success_rate:.1f}%)\n")
            
            if 'timeout' in df.columns:
                timeout_count = df['timeout'].sum()
                timeout_rate = df['timeout'].mean() * 100 if len(df) > 0 else 0
                f.write(f"   - Timeout tests: {timeout_count}/{len(df)} ({timeout_rate:.1f}%)\n")
            f.write("\n")
            
            # Details for each test
            f.write("2. DETAILED TEST RESULTS:\n")
            for _, row in df.iterrows():
                success = row.get('success', False)
                timeout = row.get('timeout', False)
                status = "✅" if success else ("⏰" if timeout else "❌")
                f.write(f"{status} {row['file_name']} ({row['solver']}) - ")
                
                if success:
                    bandwidth = row.get('bandwidth', 'N/A')
                    runtime = row.get('runtime_sec', 'N/A')
                    clauses = row.get('clauses', 'N/A')
                    f.write(f"w={bandwidth}, {runtime}s, {clauses} clauses\n")
                else:
                    error_msg = row.get('error_msg', 'No error information')
                    if pd.isna(error_msg) or error_msg is None:
                        error_msg = "No error information"
                    error_preview = str(error_msg)[:50] + "..." if len(str(error_msg)) > 50 else str(error_msg)
                    f.write(f"FAILED: {error_preview}\n")
            
            f.write("\n3. DETAILED STATISTICS:\n")
            f.write(str(df.describe().round(2)))
        
        print(f"\n📝 Detailed report saved to: {report_file}")
        
    except Exception as e:
        print(f"❌ Error creating report: {e}")
    
    # Create charts if matplotlib is available
    if PLOTTING_AVAILABLE:
        try:
            create_plots(df, timestamp)
        except Exception as e:
            print(f"❌ Error creating charts: {e}")
    else:
        print("💡 Install matplotlib to create charts: pip install matplotlib seaborn")

def create_plots(df, timestamp):
    """Create analysis charts"""
    if not PLOTTING_AVAILABLE:
        print("❌ Matplotlib not available - cannot create charts")
        return
        
    df_success = df[df['success'] == True]
    
    if df_success.empty:
        print("❌ No successful data to create charts")
        return
    
    try:
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('CBP Test Results Analysis', fontsize=16)
        
        # 1. Runtime vs Graph size
        if 'vertices' in df_success.columns and 'runtime_sec' in df_success.columns:
            # Filter valid data
            plot_data = df_success.dropna(subset=['vertices', 'runtime_sec'])
            if not plot_data.empty:
                axes[0, 0].scatter(plot_data['vertices'], plot_data['runtime_sec'], alpha=0.6)
                axes[0, 0].set_xlabel('Number of Vertices')
                axes[0, 0].set_ylabel('Runtime (seconds)')
                axes[0, 0].set_title('Runtime vs Graph Size')
            else:
                axes[0, 0].text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=axes[0, 0].transAxes)
                axes[0, 0].set_title('Runtime vs Graph Size (No Data)')
        else:
            axes[0, 0].text(0.5, 0.5, 'Missing columns', ha='center', va='center', transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('Runtime vs Graph Size (Missing Data)')
        
        # 2. Bandwidth vs Graph size
        if 'vertices' in df_success.columns and 'bandwidth' in df_success.columns:
            plot_data = df_success.dropna(subset=['vertices', 'bandwidth'])
            if not plot_data.empty:
                axes[0, 1].scatter(plot_data['vertices'], plot_data['bandwidth'], alpha=0.6, color='red')
                axes[0, 1].set_xlabel('Number of Vertices')
                axes[0, 1].set_ylabel('Bandwidth')
                axes[0, 1].set_title('Bandwidth vs Graph Size')
            else:
                axes[0, 1].text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=axes[0, 1].transAxes)
                axes[0, 1].set_title('Bandwidth vs Graph Size (No Data)')
        else:
            axes[0, 1].text(0.5, 0.5, 'Missing columns', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('Bandwidth vs Graph Size (Missing Data)')
        
        # 3. Success rate by solver
        if 'solver' in df.columns and 'success' in df.columns:
            success_rate = df.groupby('solver')['success'].mean()
            if not success_rate.empty:
                axes[1, 0].bar(success_rate.index, success_rate.values)
                axes[1, 0].set_ylabel('Success Rate')
                axes[1, 0].set_title('Success Rate by Solver')
                axes[1, 0].tick_params(axis='x', rotation=45)
            else:
                axes[1, 0].text(0.5, 0.5, 'No data', ha='center', va='center', transform=axes[1, 0].transAxes)
                axes[1, 0].set_title('Success Rate by Solver (No Data)')
        else:
            axes[1, 0].text(0.5, 0.5, 'Missing columns', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Success Rate by Solver (Missing Data)')
        
        # 4. Runtime distribution
        if 'runtime_sec' in df_success.columns:
            runtime_data = df_success['runtime_sec'].dropna()
            if not runtime_data.empty and len(runtime_data) > 1:
                axes[1, 1].hist(runtime_data, bins=min(20, len(runtime_data)), alpha=0.7)
                axes[1, 1].set_xlabel('Runtime (seconds)')
                axes[1, 1].set_ylabel('Frequency')
                axes[1, 1].set_title('Runtime Distribution')
            else:
                axes[1, 1].text(0.5, 0.5, 'Insufficient data', ha='center', va='center', transform=axes[1, 1].transAxes)
                axes[1, 1].set_title('Runtime Distribution (No Data)')
        else:
            axes[1, 1].text(0.5, 0.5, 'Missing runtime column', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Runtime Distribution (Missing Data)')
        
        plt.tight_layout()
        plot_file = f"cbp_analysis_plots_{timestamp}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"📊 Charts saved to: {plot_file}")
        plt.close()
        
    except Exception as e:
        print(f"❌ Error creating charts: {e}")
        if 'fig' in locals():
            plt.close(fig)

def main():
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = find_latest_csv()
    
    if not csv_file or not os.path.exists(csv_file):
        print("❌ CSV result file not found!")
        print("💡 Usage: python analyze_results.py <file.csv>")
        print("💡 Or place CSV file in current directory")
        return
    
    analyze_results(csv_file)

if __name__ == "__main__":
    main()
