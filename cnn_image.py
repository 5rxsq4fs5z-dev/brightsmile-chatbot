import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import urllib.request
import os

# تحميل نموذج CNN جاهز
def حمل_النموذج():
    نموذج = models.resnet18(pretrained=True)
    نموذج.eval()
    return نموذج

# معالجة الصورة
def حضر_الصورة(مسار_الصورة):
    تحويلات = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    صورة = Image.open(مسار_الصورة).convert('RGB')
    return تحويلات(صورة).unsqueeze(0)

# تحليل الصورة
def حلل_الصورة(مسار_الصورة):
    try:
        نموذج = حمل_النموذج()
        صورة = حضر_الصورة(مسار_الصورة)
        
        with torch.no_grad():
            نتيجة = نموذج(صورة)
        
        احتمالية = torch.nn.functional.softmax(نتيجة[0], dim=0)
        أعلى_قيمة = احتمالية.max().item()
        
        if أعلى_قيمة > 0.3:
            return "تم استلام صورتك ✅ سنحيلها للطبيب المختص لمراجعتها."
        else:
            return "الصورة غير واضحة، من فضلك أرسل صورة أوضح للأسنان."
    except:
        return "حدث خطأ في معالجة الصورة، حاول مرة أخرى."

print("CNN جاهز! ✅")
print(حلل_الصورة.__doc__ or "نموذج تحليل الصور شغال")