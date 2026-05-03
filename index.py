from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Görsel Arayüz (HTML & CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIP Sorgu Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background: #0f172a; color: white; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-4xl w-full glass rounded-3xl p-8 shadow-2xl">
        <div class="text-center mb-10">
            <h1 class="text-4xl font-black text-blue-500 mb-2 tracking-tighter">VIP SORGU PANELİ</h1>
            <p class="text-slate-400">Hızlı, Güvenli ve Gizli Veri Sorgulama</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Sol Taraf: Form -->
            <div class="space-y-4">
                <select id="sorguTipi" class="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                    <option value="tc">🆔 TC Sorgu</option>
                    <option value="adres">🏠 Adres Sorgu</option>
                    <option value="adsoyad">👤 Ad Soyad Sorgu</option>
                    <option value="gsmtc">📞 GSM'den TC</option>
                    <option value="tcgsm">📱 TC'den GSM</option>
                    <option value="isyeri">🏢 İş Yeri Sorgu</option>
                    <option value="sulale">👨‍👩‍👧‍👦 Sülale Sorgu</option>
                </select>

                <input type="text" id="inputVal" placeholder="Sorgulanacak veriyi girin..." class="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 outline-none focus:ring-2 focus:ring-blue-500">
                
                <div id="adsoyadEkstra" class="hidden space-y-4">
                    <input type="text" id="soyadi" placeholder="Soyadı..." class="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 outline-none">
                    <input type="text" id="il" placeholder="İl (Opsiyonel)..." class="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 outline-none">
                </div>

                <button onclick="sorgula()" id="sorguBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg transition-all transform hover:scale-[1.02]">
                    <i class="fa-solid fa-magnifying-glass mr-2"></i> SORGUYU BAŞLAT
                </button>
            </div>

            <!-- Sağ Taraf: Sonuç -->
            <div class="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                <h3 class="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">Sorgu Sonucu</h3>
                <pre id="sonuc" class="text-blue-400 font-mono text-sm whitespace-pre-wrap">Henüz sorgu yapılmadı...</pre>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('sorguTipi').addEventListener('change', function() {
            const ekstra = document.getElementById('adsoyadEkstra');
            ekstra.classList.toggle('hidden', this.value !== 'adsoyad');
        });

        async function sorgula() {
            const btn = document.getElementById('sorguBtn');
            const sonuc = document.getElementById('sonuc');
            const tip = document.getElementById('sorguTipi').value;
            const input = document.getElementById('inputVal').value;
            
            btn.innerHTML = "Sorgulanıyor...";
            btn.disabled = true;

            let url = `/api/sorgu?tip=${tip}&val=${input}`;
            if(tip === 'adsoyad') {
                url += `&soyadi=${document.getElementById('soyadi').value}&il=${document.getElementById('il').value}`;
            }

            try {
                const res = await fetch(url);
                const data = await res.json();
                sonuc.innerText = JSON.stringify(data, null, 2);
            } catch (e) {
                sonuc.innerText = "Bir hata oluştu!";
            } finally {
                btn.innerHTML = '<i class="fa-solid fa-magnifying-glass mr-2"></i> SORGUYU BAŞLAT';
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/sorgu')
def api_sorgu():
    tip = request.args.get('tip')
    val = request.args.get('val')
    
    endpoints = {
        "tc": "tc.php?tc=",
        "adres": "adres.php?tc=",
        "gsmtc": "gsmtc.php?gsm=",
        "tcgsm": "tcgsm.php?tc=",
        "isyeri": "isyeri.php?tc=",
        "sulale": "sulale.php?tc="
    }

    try:
        if tip == "adsoyad":
            soyadi = request.args.get('soyadi')
            il = request.args.get('il', '')
            url = f"https://arastir.vip/api/adsoyad.php?adi={val}&soyadi={soyadi}&il={il}"
        else:
            url = f"https://arastir.vip/api/{endpoints[tip]}{val}"
        
        r = requests.get(url, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)})

# Vercel için gerekli
def handler(event, context):
    return app(event, context)
