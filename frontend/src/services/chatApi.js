import axios from 'axios';

/**
 * API client for your n8n chat workflow.
 *
 * Configure the endpoint in a Vite env var (create `frontend/.env` if needed):
 *   VITE_N8N_CHAT_URL=https://your-n8n-host/webhook/chat
 * If not set, it falls back to `/api/chat` which you can proxy in Vite or your server.
 */
const N8N_URL ='http://localhost:5678/webhook-test/03e650c2-18be-4c37-903a-4e99bddcc8b1';

/**
 * Sends the user's message to the n8n webhook and returns markdown text.
 *
 * @param {string} userMessage - The raw message typed by the user.
 * @returns {Promise<string>} - Markdown content to render in the chat.
 *
 * Notes:
 * - We normalize different possible response shapes from n8n: plain string,
 *   `{ markdown }`, `{ result }`, or `{ message }`.
 * - If the shape is unknown, we stringify it so you still see something useful.
 * - Errors are thrown with a readable message for the UI to toast/display.
 */
export async function sendToN8n(userMessage) {
  try {
    // Adjust the payload key here if your n8n node expects another name (e.g., `prompt`).
    const res = await axios.post(N8N_URL, { message: userMessage });
    const data = res?.data[0];
    console.log(data)
    // Normalize likely shapes returned by n8n
    if (typeof data === 'string') return data; // plain markdown string
    if (data?.output) return data.output;  // { markdown: '...' }
    if (data?.result) return data.result;      // { result: '...' }
    if (data?.message) return data.message;    // { message: '...' }

    // Fallback: stringify unknown response shapes
    return typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data);
  } catch (err) {
    // Surface a readable error message to the caller/UI
    const msg = err?.response?.data?.error || err?.message || 'Unknown error';
    throw new Error(`Request failed: ${msg}`);
  }
} 