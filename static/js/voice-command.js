(function () {
  const widget = document.getElementById("voice-command-widget");
  if (!widget) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const endpoint = widget.dataset.endpoint;
  const panel = document.getElementById("voice-command-panel");
  const fab = document.getElementById("voice-command-fab");
  const close = document.getElementById("voice-command-close");
  const start = document.getElementById("voice-command-start");
  const save = document.getElementById("voice-command-save");
  const status = document.getElementById("voice-command-status");
  const transcriptNode = document.getElementById("voice-command-transcript");
  const confirmation = document.getElementById("voice-command-confirmation");
  const summary = document.getElementById("voice-command-summary");
  const isAssistantPage = window.location.pathname.startsWith("/asistente");

  let recognition = null;
  let finalTranscript = "";
  let interimTranscript = "";
  let isListening = false;
  let shouldKeepListening = false;
  let silenceTimer = null;
  let restartAttempts = 0;
  const maxRestartAttempts = 8;
  const silenceLimitMs = 12000;

  function csrfToken() {
    return document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((item) => item.startsWith("csrftoken="))
      ?.split("=")[1] || "";
  }

  function showPanel() {
    panel.classList.remove("hidden");
    fab.classList.add("is-open");
    lucide.createIcons();
  }

  function hidePanel() {
    panel.classList.add("hidden");
    fab.classList.remove("is-open", "is-listening");
    stopListening();
  }

  function setTranscript(value, isFinal) {
    transcriptNode.value = value || "";
    confirmation.classList.toggle("hidden", !isFinal || !value);
    save.disabled = !isFinal || !value;
    if (isFinal && value) summary.textContent = isAssistantPage ? `Se preguntara a la IA: "${value}"` : `Se guardara este comando: "${value}"`;
  }

  function setStartButton(listening) {
    start.innerHTML = listening
      ? '<i data-lucide="square" class="h-4 w-4"></i>Detener'
      : '<i data-lucide="mic" class="h-4 w-4"></i>Escuchar';
    lucide.createIcons();
  }

  function setRetryButton() {
    start.innerHTML = '<i data-lucide="refresh-cw" class="h-4 w-4"></i>Reintentar voz';
    lucide.createIcons();
  }

  function enableManualFallback(message) {
    shouldKeepListening = false;
    isListening = false;
    window.clearTimeout(silenceTimer);
    fab.classList.remove("is-listening");
    status.textContent = message;
    setRetryButton();
    transcriptNode.focus();
  }

  function resetSilenceTimer() {
    window.clearTimeout(silenceTimer);
    if (!isListening) return;
    silenceTimer = window.setTimeout(function () {
      status.textContent = finalTranscript.trim()
        ? "Comando reconocido. Confirma para guardar."
        : "No escuche audio. Revisa el permiso del microfono e intenta otra vez.";
      stopListening();
    }, silenceLimitMs);
  }

  function stopListening() {
    shouldKeepListening = false;
    isListening = false;
    window.clearTimeout(silenceTimer);
    fab.classList.remove("is-listening");
    setStartButton(false);
    if (recognition) {
      try {
        recognition.stop();
      } catch (error) {
        recognition.abort();
      }
    }
  }

  async function ensureMicrophonePermission() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return true;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      return true;
    } catch (error) {
      status.textContent = "El navegador no tiene permiso para usar el microfono.";
      return false;
    }
  }

  function initRecognition() {
    if (!SpeechRecognition) {
      enableManualFallback("Tu navegador no soporta Web Speech API. Escribe el comando y guardalo.");
      return null;
    }
    const instance = new SpeechRecognition();
    instance.lang = "es-CO";
    instance.interimResults = true;
    instance.continuous = true;
    instance.maxAlternatives = 1;

    instance.onstart = function () {
      status.textContent = "Escuchando...";
      isListening = true;
      fab.classList.add("is-listening");
      save.disabled = true;
      setStartButton(true);
      resetSilenceTimer();
    };

    instance.onresult = function (event) {
      interimTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalTranscript = `${finalTranscript} ${text}`.trim();
        else interimTranscript += text;
      }
      const current = `${finalTranscript} ${interimTranscript}`.trim();
      setTranscript(current, Boolean(finalTranscript.trim()));
      status.textContent = finalTranscript.trim() ? "Comando reconocido. Confirma para guardar." : "Reconociendo audio...";
      resetSilenceTimer();
    };

    instance.onerror = function (event) {
      if (event.error === "no-speech") {
        status.textContent = "Sigo escuchando. Habla cerca del microfono.";
      } else if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        enableManualFallback("Permite el microfono en el navegador o escribe el comando manualmente.");
        return;
      } else if (event.error === "network") {
        enableManualFallback("El reconocimiento de voz del navegador no esta disponible. Escribe el comando y guardalo.");
        return;
      } else {
        status.textContent = `Error de voz: ${event.error}`;
      }
      fab.classList.remove("is-listening");
      isListening = false;
      setStartButton(false);
    };

    instance.onend = function () {
      isListening = false;
      fab.classList.remove("is-listening");
      setStartButton(false);
      window.clearTimeout(silenceTimer);
      if (shouldKeepListening && !finalTranscript.trim() && restartAttempts < maxRestartAttempts) {
        restartAttempts += 1;
        window.setTimeout(function () {
          try {
            instance.start();
          } catch (error) {
            status.textContent = "No pude reiniciar el microfono. Intenta nuevamente.";
          }
        }, 350);
        return;
      }
      if (!finalTranscript.trim() && shouldKeepListening) {
        status.textContent = "No se detecto un comando. Intenta hablar apenas pulses Escuchar.";
      }
      shouldKeepListening = false;
    };

    return instance;
  }

  async function saveCommand() {
    const command = (transcriptNode.value || finalTranscript).trim();
    if (!command) return;
    if (isAssistantPage) {
      window.dispatchEvent(new CustomEvent("consultapp:ask-ai", { detail: { question: command } }));
      status.textContent = "Pregunta enviada al asistente.";
      setTimeout(hidePanel, 500);
      return;
    }
    save.disabled = true;
    status.textContent = "Guardando movimiento...";
    const response = await fetch(endpoint, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken(),
      },
      body: JSON.stringify({ command }),
    });
    const payload = await response.json();
    if (payload.success) {
      status.textContent = payload.message || "Movimiento registrado.";
      summary.textContent = `${payload.type === "expense" ? "Gasto" : "Ingreso"} · ${payload.category_name || payload.category} · $${Number(payload.amount).toLocaleString("es-CO")}`;
      setTimeout(() => window.location.reload(), 900);
    } else {
      status.textContent = payload.message || "No se pudo interpretar el comando.";
      save.disabled = false;
    }
  }

  fab.addEventListener("click", showPanel);
  close.addEventListener("click", hidePanel);
  start.addEventListener("click", async function () {
    showPanel();
    if (isListening) {
      stopListening();
      status.textContent = finalTranscript.trim() ? "Comando reconocido. Confirma para guardar." : "Escucha detenida.";
      return;
    }
    const hasPermission = await ensureMicrophonePermission();
    if (!hasPermission) return;
    finalTranscript = "";
    interimTranscript = "";
    restartAttempts = 0;
    shouldKeepListening = true;
    setTranscript("", false);
    recognition = recognition || initRecognition();
    if (recognition) {
      try {
        recognition.start();
      } catch (error) {
        status.textContent = "El microfono ya esta iniciando. Espera un momento.";
      }
    }
  });
  save.addEventListener("click", saveCommand);
  transcriptNode.addEventListener("input", function () {
    const command = transcriptNode.value.trim();
    finalTranscript = command;
    confirmation.classList.toggle("hidden", !command);
    save.disabled = !command;
    if (command) summary.textContent = isAssistantPage ? `Se preguntara a la IA: "${command}"` : `Se guardara este comando: "${command}"`;
  });
  if (isAssistantPage) {
    status.textContent = "Pulsa el microfono para preguntarle al asistente financiero.";
    summary.textContent = "";
  }
})();
