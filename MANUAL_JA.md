# RoomVerse Node 利用マニュアル

このマニュアルでは、配布された `RoomVerseNode.exe` のセットアップ方法と使い方について説明します。

## 1. 準備（Prerequisites）

RoomVerseを動かすには、以下の準備が必要です。

### ローカルLLMの用意
RoomVerse自体にはAIモデルは内蔵されていません。ご自身のPCで動作するLLM（大規模言語モデル）サーバーが必要です。
以下のいずれかをインストールし、起動しておいてください。

*   **Ollama** (推奨): [https://ollama.com/](https://ollama.com/)
    *   インストール後、`ollama run llama3` 等でモデルをダウンロード・起動してください。
    *   デフォルト設定でOKです（通常 `http://localhost:11434` で動作します）。
*   **LM Studio**: [https://lmstudio.ai/](https://lmstudio.ai/)
    *   Local Server機能を開始してください。
    *   「CORS」の設定をONにする必要がある場合があります。

※ llama.cpp, Kobold.cpp, Oobabooga など、LLMモデルを読み込めて、OpenAI API互換のサーバーを利用できるソフトウェアであれば、理論上は動作するはずです。

## 2. インストールと起動

1.  **配置**: `RoomVerseNode.exe` を、専用のフォルダ（例: `C:\Games\RoomVerse`）に置いてください。
    *   ※起動時に設定ファイルやログファイルが生成されるため、デスクトップに直接置くよりフォルダを作ることをお勧めします。
2.  **起動**: `RoomVerseNode.exe` をダブルクリックして起動します。
3.  **初期化**:
    *   黒い画面（コンソール）が表示されます。
    *   初回のみ、通信用ツール (`cloudflared`) のダウンロードが自動的に行われる場合があります。完了するまでお待ちください。
    *   Windowsファイアウォールの警告が出た場合は、「アクセスを許可」してください。

コンソールに `Uvicorn running on http://0.0.0.0:22022` のような表示が出れば起動完了です。
**この黒い画面は閉じずに、最小化しておいてください。**

## 3. 設定（Dashboard）

1.  ブラウザを開き、以下のURLにアクセスします。
    *   [http://localhost:22022/dashboard](http://localhost:22022/dashboard)
2.  **キャラクター設定**:
    *   Character Settingsを開き、AIの名前や性格（Persona）を入力します。
    *   設定したら「Save Configuration」を押します。
3.  **LLM接続**:
    *   LLM Settingsで「Scan」ボタンを押すと、起動中のOllamaなどを自動検出できます。
    *   手動入力の場合は `http://localhost:11434/v1` (Ollama) 等を入力してください。
4.  **Lorebook（用語集）**:
    *   Loreタブで、あなたの世界観や専門用語を登録できます。
    *   「Teach」ボタンからAIに言葉を教えることも可能です。

## 4. オンライン公開

他の人のルームを訪問したり、誰かを招き入れたりするには「公開」が必要です。

1.  **Room & Discovery** 設定を開きます。
2.  「Auto-Publish to Discovery」にチェックを入れ、「Save」します。
3.  Lobbyタブを開き、他のルームが表示されれば接続成功です！

## 5. 終了方法

黒いコンソール画面を閉じる（右上の×ボタン）と、アプリケーションは終了します。
次回起動時は、同じフォルダの設定ファイルを読み込んで再開します。

## トラブルシューティング

*   **画面が開かない**: コンソールがエラーで止まっていないか確認してください。
*   **LLMにつながらない**: Ollama等が裏で動いているか確認してください。
*   **公開できない**: インターネット接続を確認してください。Cloudflare Tunnelの接続には数秒～数十秒かかる場合があります。

---
Enjoy your RoomVerse!
