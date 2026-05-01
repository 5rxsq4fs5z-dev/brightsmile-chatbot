import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Arial'
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# بيانات وهمية واقعية
أسماء_ذكور = ['محمد', 'أحمد', 'خالد', 'عبدالله', 'يوسف', 'عمر', 'سعد', 'فيصل', 'تركي', 'ماجد']
أسماء_إناث = ['فاطمة', 'سارة', 'نورة', 'منى', 'هند', 'ريم', 'لمى', 'دانة', 'رنا', 'أميرة']
أسماء = أسماء_ذكور + أسماء_إناث

خدمات_وأسعار = {
    'كشف': 150,
    'حشو': 300,
    'خلع': 250,
    'تنظيف': 200,
    'تبييض': 800,
    'تقويم': 5000,
    'زرعات': 8000,
    'ابتسامة هوليود': 15000,
    'علاج عصب': 600,
    'تركيب تاج': 1200
}

أطباء = ['د. سارة', 'د. خالد']
أيام = ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']

# توليد 1000 سجل
بيانات = []
تاريخ_بداية = datetime(2024, 1, 1)

for i in range(1000):
    خدمة = random.choice(list(خدمات_وأسعار.keys()))
    سعر_أساسي = خدمات_وأسعار[خدمة]
    تاريخ = تاريخ_بداية + timedelta(days=random.randint(0, 364))
    
    بيانات.append({
        'رقم_المريض': i + 1,
        'اسم_المريض': random.choice(أسماء),
        'العمر': random.randint(8, 75),
        'الجنس': random.choice(['ذكر', 'أنثى']),
        'الخدمة': خدمة,
        'الطبيب': random.choice(أطباء),
        'السعر': سعر_أساسي,
        'الشهر': تاريخ.month,
        'اليوم': random.choice(أيام),
        'الوقت': random.choice(['صباح', 'ظهر', 'مساء']),
        'الرضا': random.choices([3, 4, 5], weights=[10, 30, 60])[0],
        'زيارة_أولى': random.choice([True, False]),
        'التاريخ': تاريخ
    })

df = pd.DataFrame(بيانات)

# الإحصاء الوصفي
print("=" * 50)
print("  إحصائيات عيادة برايت سمايل 🦷")
print("=" * 50)
print(f"\n📊 إجمالي المرضى: {len(df)}")
print(f"👥 مرضى جدد: {df['زيارة_أولى'].sum()}")
print(f"🔄 مرضى متكررون: {(~df['زيارة_أولى']).sum()}")
print(f"👤 متوسط العمر: {df['العمر'].mean():.1f} سنة")
print(f"💰 إجمالي الإيرادات: {df['السعر'].sum():,} ريال")
print(f"💵 متوسط سعر الخدمة: {df['السعر'].mean():.0f} ريال")
print(f"⭐ متوسط الرضا: {df['الرضا'].mean():.1f} من 5")

print(f"\n🏆 أكثر الخدمات طلباً:")
print(df['الخدمة'].value_counts().head(5).to_string())

print(f"\n👨‍⚕️ إيرادات الأطباء:")
print(df.groupby('الطبيب')['السعر'].sum().apply(lambda x: f"{x:,} ريال").to_string())

print(f"\n📅 أكثر الأيام ازدحاماً:")
print(df['اليوم'].value_counts().head(3).to_string())

print(f"\n⏰ أكثر الأوقات ازدحاماً:")
print(df['الوقت'].value_counts().to_string())

# رسوم بيانية
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('Brighton Smile Clinic - Statistics 2024', fontsize=16, fontweight='bold')

# 1 - أكثر الخدمات
df['الخدمة'].value_counts().plot(kind='bar', ax=axes[0,0], color='teal')
axes[0,0].set_title('Most Requested Services')
axes[0,0].set_xlabel('Service')
axes[0,0].set_ylabel('Count')
axes[0,0].tick_params(axis='x', rotation=45)

# 2 - الإيرادات الشهرية
شهري = df.groupby('الشهر')['السعر'].sum()
شهري.plot(kind='line', ax=axes[0,1], color='blue', marker='o')
axes[0,1].set_title('Monthly Revenue')
axes[0,1].set_xlabel('Month')
axes[0,1].set_ylabel('Revenue (SAR)')

# 3 - توزيع الأعمار
df['العمر'].hist(ax=axes[0,2], bins=10, color='orange', edgecolor='black')
axes[0,2].set_title('Patient Age Distribution')
axes[0,2].set_xlabel('Age')
axes[0,2].set_ylabel('Count')

# 4 - إيرادات الأطباء
df.groupby('الطبيب')['السعر'].sum().plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
axes[1,0].set_title('Doctor Revenue Share')

# 5 - توزيع الرضا
df['الرضا'].value_counts().sort_index().plot(kind='bar', ax=axes[1,1], color='green')
axes[1,1].set_title('Patient Satisfaction')
axes[1,1].set_xlabel('Rating')
axes[1,1].set_ylabel('Count')

# 6 - الأيام
df['اليوم'].value_counts().plot(kind='bar', ax=axes[1,2], color='purple')
axes[1,2].set_title('Busy Days')
axes[1,2].set_xlabel('Day')
axes[1,2].set_ylabel('Count')
axes[1,2].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('clinic_stats.png', dpi=150, bbox_inches='tight')
print("\n✅ تم حفظ الرسوم البيانية في clinic_stats.png")

# حفظ البيانات
df.to_csv('clinic_data.csv', index=False, encoding='utf-8-sig')
print("✅ تم حفظ البيانات في clinic_data.csv")