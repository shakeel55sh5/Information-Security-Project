// CovertPixel Application Logic

document.addEventListener('DOMContentLoaded', () => {
    // State Variables
    let currentImageId = null;
    let currentImageWidth = 0;
    let currentImageHeight = 0;
    const delimiterLength = 9; // "###END###" is 9 characters

    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const generateSampleBtn = document.getElementById('generate-sample-btn');
    
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    const secretMessageTextarea = document.getElementById('secret-message');
    const payloadSizeEl = document.getElementById('payload-size');
    const maxCapacityEl = document.getElementById('max-capacity');
    const capacityFillEl = document.getElementById('capacity-fill');
    
    const encodeBtn = document.getElementById('encode-btn');
    const decodeBtn = document.getElementById('decode-btn');
    const detectBtn = document.getElementById('detect-btn');
    
    const originalPreviewBox = document.getElementById('original-preview-box');
    const originalPreviewImg = document.getElementById('original-preview-img');
    const originalMeta = document.getElementById('original-meta');
    const origMetaName = document.getElementById('orig-meta-name');
    const origMetaDim = document.getElementById('orig-meta-dim');
    
    const processedPreviewBox = document.getElementById('processed-preview-box');
    const processedPreviewImg = document.getElementById('processed-preview-img');
    const processedMeta = document.getElementById('processed-meta');
    const procMetaName = document.getElementById('proc-meta-name');
    const downloadLink = document.getElementById('download-link');
    const processedLabel = document.getElementById('processed-label');
    
    const consoleBox = document.getElementById('console-box');

    // Terminal Logger
    function log(message, type = 'system') {
        const line = document.createElement('div');
        line.classList.add('console-line', `${type}-msg`);
        
        const timestamp = new Date().toLocaleTimeString();
        line.innerText = `[${timestamp}] > ${message}`;
        
        consoleBox.appendChild(line);
        consoleBox.scrollTop = consoleBox.scrollHeight;
    }

    // Drag and Drop event listeners
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // Operation Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active to clicked tab
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            log(`Switched view to: ${btn.innerText.trim()}`);
        });
    });

    // Generate Sample Image Button
    generateSampleBtn.addEventListener('click', async () => {
        try {
            generateSampleBtn.disabled = true;
            log('Requesting sample clean image generation...');
            
            const response = await fetch('/generate_sample', { method: 'POST' });
            if (!response.ok) throw new Error('Failed to generate sample image');
            
            const data = await response.json();
            currentImageId = data.image_id;
            
            // Set image source and trigger load event to get dimensions
            originalPreviewImg.src = data.image_url;
            originalPreviewImg.onload = () => {
                currentImageWidth = originalPreviewImg.naturalWidth;
                currentImageHeight = originalPreviewImg.naturalHeight;
                
                // Update UI elements
                originalPreviewBox.classList.remove('empty');
                originalPreviewImg.classList.remove('hidden');
                originalMeta.classList.remove('hidden');
                origMetaName.innerText = data.filename;
                origMetaDim.innerText = `${currentImageWidth}x${currentImageHeight}`;
                
                // Clear processed output
                clearProcessedView();
                
                // Recalculate capacity
                const maxChars = Math.floor((currentImageWidth * currentImageHeight * 3) / 8) - delimiterLength;
                maxCapacityEl.innerText = `${maxChars} chars`;
                
                log(`Sample image loaded: ${data.filename} (${currentImageWidth}x${currentImageHeight})`, 'success');
                enableActionButtons();
                updateCapacityInfo();
            };
        } catch (error) {
            log(`Error: ${error.message}`, 'error');
        } finally {
            generateSampleBtn.disabled = false;
        }
    });

    // Upload & Handle Selected File
    async function handleFileSelection(file) {
        if (!file.type.match('image.*')) {
            log('Error: File must be a valid PNG, JPG, or JPEG image.', 'error');
            return;
        }
        
        try {
            log(`Uploading image: ${file.name}...`);
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload_image', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Image upload failed');
            }
            
            const data = await response.json();
            currentImageId = data.image_id;
            
            // Display Image Preview and obtain dimensions
            originalPreviewImg.src = data.image_url;
            originalPreviewImg.onload = () => {
                currentImageWidth = originalPreviewImg.naturalWidth;
                currentImageHeight = originalPreviewImg.naturalHeight;
                
                // Update UI elements
                originalPreviewBox.classList.remove('empty');
                originalPreviewImg.classList.remove('hidden');
                originalMeta.classList.remove('hidden');
                origMetaName.innerText = file.name;
                origMetaDim.innerText = `${currentImageWidth}x${currentImageHeight}`;
                
                // Clear processed output
                clearProcessedView();
                
                // Recalculate capacity
                const maxChars = Math.floor((currentImageWidth * currentImageHeight * 3) / 8) - delimiterLength;
                maxCapacityEl.innerText = `${maxChars} chars`;
                
                log(`Image uploaded successfully. ID: ${currentImageId.substring(0,8)}...`, 'success');
                enableActionButtons();
                updateCapacityInfo();
            };
        } catch (error) {
            log(`Upload Error: ${error.message}`, 'error');
        }
    }

    // Helper functions
    function enableActionButtons() {
        encodeBtn.disabled = false;
        decodeBtn.disabled = false;
        detectBtn.disabled = false;
    }

    function clearProcessedView() {
        processedPreviewBox.classList.add('empty');
        processedPreviewImg.classList.add('hidden');
        processedPreviewImg.src = '';
        processedMeta.classList.add('hidden');
    }

    // Capacity Tracker
    secretMessageTextarea.addEventListener('input', updateCapacityInfo);

    function updateCapacityInfo() {
        if (!currentImageId) return;
        
        const text = secretMessageTextarea.value;
        const size = text.length;
        payloadSizeEl.innerText = size;
        
        const maxChars = Math.floor((currentImageWidth * currentImageHeight * 3) / 8) - delimiterLength;
        const percentage = Math.min((size / maxChars) * 100, 100);
        
        capacityFillEl.style.width = `${percentage}%`;
        
        // Color updates based on capacity
        capacityFillEl.classList.remove('warning', 'danger');
        if (percentage >= 90) {
            capacityFillEl.classList.add('danger');
        } else if (percentage >= 70) {
            capacityFillEl.classList.add('warning');
        }
        
        // Enable or disable encode button
        if (size > 0 && size <= maxChars) {
            encodeBtn.disabled = false;
        } else {
            encodeBtn.disabled = true;
        }
    }

    // Operations Handlers: ENCODE
    encodeBtn.addEventListener('click', async () => {
        const message = secretMessageTextarea.value.trim();
        if (!message || !currentImageId) return;
        
        try {
            encodeBtn.disabled = true;
            log('Encoding secret message into image pixels...');
            
            const params = new URLSearchParams({
                image_id: currentImageId,
                secret_message: message
            });
            
            const response = await fetch(`/encode_image?${params.toString()}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Encoding failed');
            }
            
            const data = await response.json();
            
            // Display encoded image in workspace display
            processedLabel.innerText = "Encoded (Stego) Image";
            processedPreviewImg.src = data.image_url;
            processedPreviewImg.onload = () => {
                processedPreviewBox.classList.remove('empty');
                processedPreviewImg.classList.remove('hidden');
                processedMeta.classList.remove('hidden');
                procMetaName.innerText = `covert_${currentImageId.substring(0,6)}.png`;
                downloadLink.href = data.image_url;
                downloadLink.setAttribute('download', `covert_${currentImageId.substring(0,6)}.png`);
                
                log(`Message hidden successfully! Saved as PNG to preserve LSB bits.`, 'success');
                log(`Stego Image ID: ${data.encoded_image_id.substring(0,8)}...`, 'success');
            };
        } catch (error) {
            log(`Encoding Error: ${error.message}`, 'error');
        } finally {
            encodeBtn.disabled = false;
        }
    });

    // Operations Handlers: DECODE
    decodeBtn.addEventListener('click', async () => {
        if (!currentImageId) return;
        
        try {
            decodeBtn.disabled = true;
            log('Decoding image. Extracting LSB bit streams...');
            
            const response = await fetch(`/decode_image?image_id=${currentImageId}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Decoding failed');
            }
            
            const data = await response.json();
            if (data.decoded_message) {
                log('Extraction Complete. Hidden message identified.', 'success');
                log(`DECRYPTED PAYLOAD: "${data.decoded_message}"`, 'success');
            } else {
                log('Extraction Complete. No valid delimiter (###END###) detected. The image appears clean.', 'warning');
            }
        } catch (error) {
            log(`Decoding Error: ${error.message}`, 'error');
        } finally {
            decodeBtn.disabled = false;
        }
    });

    // Operations Handlers: DETECT / STEGANALYSIS
    detectBtn.addEventListener('click', async () => {
        if (!currentImageId) return;
        
        try {
            detectBtn.disabled = true;
            log('Scanning image signatures. Running LSB heuristic checks...');
            
            const response = await fetch(`/analyze_image?image_id=${currentImageId}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Analysis failed');
            }
            
            const data = await response.json();
            if (data.is_hidden) {
                log('STEGANOGRAPHY DETECTED!', 'error');
                log(`[ALERT] Hidden payload signature matched: "${data.decoded_message}"`, 'error');
            } else {
                log('STEG-CHECK PASSED: No hidden message signatures found.', 'success');
            }
        } catch (error) {
            log(`Analysis Error: ${error.message}`, 'error');
        } finally {
            detectBtn.disabled = false;
        }
    });
});
