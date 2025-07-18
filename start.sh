#!/data/data/com.termux/files/usr/bin/bash


SCRIPT="murbugwa.py"


if [ ! -f "$SCRIPT" ]; then
    echo "❌ File $SCRIPT tidak ditemukan!"
    exit 1
fi


LOGFILE="murbugwa.log"


nohup python "$SCRIPT" > "$LOGFILE" 2>&1 &

echo "✅ Murbug Loading Tunggu Sebentar😅"
echo "📄 Hubungi t.me@MirayyLev Untuk Perbaikan"
