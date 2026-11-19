import { initializeApp } from "https://www.gstatic.com/firebasejs/13.4.0/firebase-app.js";
import {
  initializeFirestore, persistentLocalCache, persistentMultipleTabManager,
  collection, addDoc, serverTimestamp, query, orderBy, limit, onSnapshot
} from "https://www.gstatic.com/firebasejs/13.4.0/firebase-firestore.js";

// Public web config (not a secret). Access is protected by firestore.rules.
const firebaseConfig = {
  apiKey: "AIzaSyDEqOdwdyJmmRSyzqP9PfkxWT90w5bC6OE",
  authDomain: "oop-exercise2.firebaseapp.com",
  projectId: "oop-exercise2",
  storageBucket: "oop-exercise2.firebasestorage.app",
  messagingSenderId: "913574707847",
  appId: "1:913574707847:web:5cf2e324d2c711fd0aee22"
};

const app = initializeApp(firebaseConfig);
// Local cache (IndexedDB): messages sent offline are kept on the device, even if the tab or the browser is closed,
// and are sent the next time the page is opened with a network connection.
// The page itself does not load without a network (there is no Service Worker).
const db = initializeFirestore(app, {
  localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() })
});

const messages = collection(db, "test-messages");
const device = /Android|iPhone|iPad/i.test(navigator.userAgent) ? "phone" : "computer";
const firstSeen = new Map(); // message id -> time this device first saw it saved on the server

const form = document.getElementById("form");
const input = document.getElementById("text");
const list = document.getElementById("list");
const net = document.getElementById("net");

function showNetwork() {
  net.textContent = navigator.onLine ? "Online" : "Offline";
  net.className = navigator.onLine ? "on" : "off";
}
window.addEventListener("online", showNetwork);
window.addEventListener("offline", showNetwork);
showNetwork();
document.getElementById("device").textContent = device;

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  // Not awaited: when offline, the promise resolves only after the server confirms
  addDoc(messages, { text, device, clientTime: Date.now(), createdAt: serverTimestamp() })
    .catch((err) => alert("Send failed: " + err.message));
  input.value = "";
});

const q = query(messages, orderBy("clientTime", "desc"), limit(50));
onSnapshot(q, { includeMetadataChanges: true }, (snap) => {
  list.innerHTML = "";
  snap.forEach((doc) => {
    const m = doc.data();
    const pending = doc.metadata.hasPendingWrites;
    if (!pending && !firstSeen.has(doc.id)) firstSeen.set(doc.id, Date.now());
    // The delay compares the sender's clock with this device's clock.
    // The two clocks are not perfectly in sync, so the delay is not fully accurate.
    const delay = firstSeen.has(doc.id) ? ((firstSeen.get(doc.id) - m.clientTime) / 1000).toFixed(2) + "s" : "";
    const li = document.createElement("li");
    li.textContent = `${pending ? "⏳ pending" : "✓ saved"} | from ${m.device} | ${delay} | ${m.text}`;
    list.appendChild(li);
  });
});
