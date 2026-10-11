/**
 * BẤT ĐỘNG SẢN ĐÀ LẠT - CLIENT JAVASCRIPT
 */

document.addEventListener('DOMContentLoaded', () => {
  initImageGallery();
  initLightbox();
  initFilterTabs();
  initToast();
  initImageFallbacks();
  initMobileFilterDrawer();
  initTouchSwipe();
  initScrollToTop();
});

/* ==========================================================================
   IMAGE GALLERY & THUMBNAILS
   ========================================================================== */
let galleryImages = [];
let currentGalleryIndex = 0;

function initImageGallery() {
  const mainImg = document.getElementById('galleryMainImage');
  const thumbs = document.querySelectorAll('.thumb-item');
  const prevBtn = document.getElementById('galleryPrevBtn');
  const nextBtn = document.getElementById('galleryNextBtn');

  if (!mainImg) return;

  // Thu thập danh sách ảnh
  galleryImages = Array.from(thumbs).map(t => t.dataset.full);
  if (galleryImages.length === 0 && mainImg.src) {
    galleryImages = [mainImg.src];
  }

  function setMainImage(index) {
    if (index < 0) index = galleryImages.length - 1;
    if (index >= galleryImages.length) index = 0;

    currentGalleryIndex = index;
    mainImg.style.opacity = '0.4';

    setTimeout(() => {
      mainImg.src = galleryImages[currentGalleryIndex];
      mainImg.style.opacity = '1';
    }, 120);

    thumbs.forEach((thumb, i) => {
      if (i === currentGalleryIndex) {
        thumb.classList.add('active');
        thumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      } else {
        thumb.classList.remove('active');
      }
    });

    const counterBadge = document.getElementById('galleryCounterBadge');
    if (counterBadge && galleryImages.length > 0) {
      counterBadge.textContent = `📷 ${currentGalleryIndex + 1} / ${galleryImages.length}`;
    }
  }

  thumbs.forEach((thumb, i) => {
    thumb.addEventListener('click', () => setMainImage(i));
  });

  if (prevBtn) {
    prevBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      setMainImage(currentGalleryIndex - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      setMainImage(currentGalleryIndex + 1);
    });
  }
}

/* ==========================================================================
   LIGHTBOX FULLSCREEN MODAL
   ========================================================================== */
function initLightbox() {
  const lightbox = document.getElementById('lightboxModal');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxClose = document.getElementById('lightboxClose');
  const lightboxCounter = document.getElementById('lightboxCounter');
  const mainGallery = document.querySelector('.gallery-main');
  const prevBtn = document.getElementById('lightboxPrevBtn');
  const nextBtn = document.getElementById('lightboxNextBtn');

  if (!lightbox || !lightboxImg) return;

  function updateLightbox() {
    lightboxImg.src = galleryImages[currentGalleryIndex];
    if (lightboxCounter) {
      lightboxCounter.textContent = `${currentGalleryIndex + 1} / ${galleryImages.length}`;
    }
  }

  function openLightbox(index) {
    if (galleryImages.length === 0) return;
    currentGalleryIndex = index;
    updateLightbox();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (mainGallery) {
    mainGallery.addEventListener('click', () => openLightbox(currentGalleryIndex));
  }

  if (lightboxClose) {
    lightboxClose.addEventListener('click', closeLightbox);
  }

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox || e.target.classList.contains('lightbox-content')) {
      closeLightbox();
    }
  });

  if (prevBtn) {
    prevBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      currentGalleryIndex = (currentGalleryIndex - 1 + galleryImages.length) % galleryImages.length;
      updateLightbox();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      currentGalleryIndex = (currentGalleryIndex + 1) % galleryImages.length;
      updateLightbox();
    });
  }

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft' && prevBtn) prevBtn.click();
    if (e.key === 'ArrowRight' && nextBtn) nextBtn.click();
  });
}

/* ==========================================================================
   FILTER TABS & DYNAMIC FILTER GROUPS
   ========================================================================== */
let filterConfigsCache = null;

function getFilterConfigs() {
  if (filterConfigsCache) return filterConfigsCache;
  const configElem = document.getElementById('filterConfigsData');
  if (configElem) {
    try {
      filterConfigsCache = JSON.parse(configElem.textContent);
    } catch (e) {
      console.error('Không thể đọc cấu hình bộ lọc:', e);
    }
  }
  return filterConfigsCache || {};
}

function updateFilterGroups(transType, preservePriceId = null) {
  const configs = getFilterConfigs();
  const config = configs[transType] || configs['all'] || configs['sale'];
  if (!config) return;

  // 1. Cập nhật nhãn và danh sách mức giá (Price Range)
  const priceLabel = document.getElementById('filterPriceLabel');
  const priceSelect = document.getElementById('filterPrice');
  const priceGroup = document.getElementById('filterGroupPrice');

  if (priceLabel && config.price_label) {
    priceLabel.textContent = config.price_label;
  }

  if (priceSelect && Array.isArray(config.price_ranges)) {
    const targetValue = preservePriceId !== null ? preservePriceId : '';
    
    // Tạo lại các options cho select mức giá
    let optionsHtml = '<option value="">Tất cả mức giá</option>';
    let valueMatched = false;

    config.price_ranges.forEach(pr => {
      const isSelected = targetValue && pr.id === targetValue;
      if (isSelected) valueMatched = true;
      optionsHtml += `<option value="${pr.id}" ${isSelected ? 'selected' : ''}>${pr.label}</option>`;
    });

    priceSelect.innerHTML = optionsHtml;
    if (!valueMatched) {
      priceSelect.value = '';
    }

    // Hiệu ứng phản hồi thị giác khi chuyển tab
    if (priceGroup) {
      priceGroup.classList.remove('filter-group-updated');
      void priceGroup.offsetWidth; // Buộc trình duyệt tính toán lại layout (reflow)
      priceGroup.classList.add('filter-group-updated');
      setTimeout(() => {
        priceGroup.classList.remove('filter-group-updated');
      }, 500);
    }
  }

  // 2. Cập nhật placeholder cho ô tìm kiếm
  const searchInput = document.getElementById('searchKeyword');
  if (searchInput && config.search_placeholder) {
    searchInput.placeholder = config.search_placeholder;
  }
}

function initFilterTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const transInput = document.getElementById('filterTrans');

  if (!tabs.length || !transInput) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const newTrans = tab.dataset.trans;
      if (tab.classList.contains('active')) return;

      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      transInput.value = newTrans;

      // Điều chỉnh các filter-group cho phù hợp với loại giao dịch mới
      updateFilterGroups(newTrans, '');
    });
  });
}

function resetFilters() {
  window.location.href = '/';
}

/* ==========================================================================
   TOAST FEEDBACK
   ========================================================================== */
function initToast() {
  // Global Toast function
  window.showToast = function(message) {
    let toast = document.getElementById('toastNotification');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toastNotification';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<span style="color:var(--primary-light)">✓</span> ${message}`;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  };
}

/**
 * Sao chép văn bản vào Clipboard tương thích 100% với iPhone (iOS Safari), Android và Desktop:
 * - Khắc phục hoàn toàn lỗi rỗng clipboard trên iOS Safari
 * - Tương thích cả kết nối mạng nội bộ HTTP (không có HTTPS / Insecure Context)
 * - Tích hợp Mobile Copy Sheet dự phòng trực quan nếu trình duyệt chặn hoàn toàn execCommand
 */
window.copyTextToClipboard = async function(text, successMsg = 'Đã sao chép vào bộ nhớ tạm!') {
  if (!text) return false;

  let success = false;

  // 1. Thử Async Clipboard API nếu trong Secure Context và được hỗ trợ
  if (window.isSecureContext && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
    try {
      await navigator.clipboard.writeText(text);
      success = true;
    } catch (err) {
      console.warn('Clipboard API thất bại, chuyển sang phương thức dự phòng...', err);
      success = false;
    }
  }

  // 2. Phương thức Textarea trực tiếp cho iOS Safari & Android (CHỈNH SỬA CHUẨN: KHÔNG dùng selectNodeContents trên textarea!)
  if (!success) {
    const ta = document.createElement('textarea');
    ta.value = text;
    // Đặt trong viewport hiện tại (tránh bị iOS coi là off-screen)
    ta.style.position = 'fixed';
    ta.style.top = '10px';
    ta.style.left = '10px';
    ta.style.width = '20px';
    ta.style.height = '20px';
    ta.style.padding = '0';
    ta.style.border = 'none';
    ta.style.outline = 'none';
    ta.style.background = 'transparent';
    ta.style.opacity = '0.01'; // Tránh Safari coi là invisible
    ta.style.fontSize = '16px'; // Ngăn Safari tự phóng to màn hình
    ta.style.zIndex = '99999';
    ta.setAttribute('readonly', '');

    document.body.appendChild(ta);

    // Xóa vùng chọn văn bản cũ của trang
    const winSel = window.getSelection();
    if (winSel) {
      winSel.removeAllRanges();
    }

    // Chọn nội dung trên textarea bằng native API
    ta.focus();
    ta.select();
    ta.setSelectionRange(0, text.length);

    try {
      success = document.execCommand('copy');
    } catch (err) {
      console.warn('execCommand với textarea lỗi:', err);
      success = false;
    }

    document.body.removeChild(ta);
  }

  // 3. Phương thức DIV ContentEditable (dành riêng cho các bản iOS Safari yêu cầu Range DOM)
  if (!success) {
    const div = document.createElement('div');
    div.contentEditable = 'true';
    div.innerText = text;
    div.style.position = 'fixed';
    div.style.top = '10px';
    div.style.left = '10px';
    div.style.width = '20px';
    div.style.height = '20px';
    div.style.padding = '0';
    div.style.border = 'none';
    div.style.background = 'transparent';
    div.style.opacity = '0.01';
    div.style.fontSize = '16px';
    div.style.zIndex = '99999';

    document.body.appendChild(div);

    const range = document.createRange();
    range.selectNodeContents(div); // Ở đây div có text nodes nên range chọn chính xác toàn bộ chữ!
    const winSel = window.getSelection();
    if (winSel) {
      winSel.removeAllRanges();
      winSel.addRange(range);
    }

    try {
      success = document.execCommand('copy');
    } catch (err) {
      console.warn('execCommand với div contentEditable lỗi:', err);
      success = false;
    }

    if (winSel) {
      winSel.removeAllRanges();
    }
    document.body.removeChild(div);
  }

  // 4. Nếu trình duyệt chặn hoàn toàn tự động sao chép (iOS 17+ mạng LAN HTTP) -> Mở Mobile Copy Sheet
  if (!success) {
    showMobileCopySheet(text, successMsg);
    return false;
  }

  if (success && window.showToast) {
    window.showToast(successMsg);
  }

  return success;
};

/**
 * Mở bảng sao chép di động chuyên dụng cho iOS Safari khi các lệnh ngầm bị chặn
 */
function showMobileCopySheet(text, successMsg) {
  let modal = document.getElementById('mobileCopyModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'mobileCopyModal';
    modal.className = 'mobile-copy-modal';
    modal.innerHTML = `
      <div class="mobile-copy-backdrop" onclick="closeMobileCopyModal()"></div>
      <div class="mobile-copy-sheet">
        <div class="mobile-copy-header">
          <div class="mobile-copy-title-row">
            <span class="mobile-copy-icon">📋</span>
            <span class="mobile-copy-title">Sao chép văn bản</span>
          </div>
          <button type="button" class="mobile-copy-close-btn" onclick="closeMobileCopyModal()" aria-label="Đóng">✕</button>
        </div>
        <p class="mobile-copy-help">Bấm nút bên dưới để tự động sao chép, hoặc nhấn giữ ô chữ rồi chọn <b>Sao chép (Copy)</b>:</p>
        <textarea id="mobileCopyArea" class="mobile-copy-textarea" readonly></textarea>
        <div class="mobile-copy-actions">
          <button type="button" class="btn-copy-sheet-select" onclick="selectAndCopyMobileArea()">
            📋 Sao Chép Ngay
          </button>
          <button type="button" class="btn-copy-sheet-done" onclick="closeMobileCopyModal()">
            Đóng
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  const area = document.getElementById('mobileCopyArea');
  if (area) {
    area.value = text;
  }
  modal.classList.add('active');

  // Tự động focus và bôi đen sẵn toàn bộ văn bản
  setTimeout(() => {
    if (area) {
      area.focus();
      area.select();
      area.setSelectionRange(0, text.length);
      try {
        const ok = document.execCommand('copy');
        if (ok && window.showToast) {
          window.showToast('✓ Đã sao chép vào bộ nhớ tạm!');
        }
      } catch (e) {}
    }
  }, 150);
}

window.selectAndCopyMobileArea = function() {
  const area = document.getElementById('mobileCopyArea');
  if (!area) return;
  area.focus();
  area.select();
  area.setSelectionRange(0, area.value.length);
  try {
    const ok = document.execCommand('copy');
    if (ok) {
      if (window.showToast) window.showToast('✓ Đã sao chép thành công!');
      setTimeout(closeMobileCopyModal, 600);
      return;
    }
  } catch (e) {}
  if (window.showToast) {
    window.showToast('Vui lòng chạm vào "Sao chép" trên thanh menu màu đen hiện ra');
  }
};

window.closeMobileCopyModal = function() {
  const modal = document.getElementById('mobileCopyModal');
  if (modal) {
    modal.classList.remove('active');
  }
};

function copyCurrentLink() {
  // Nếu là thiết bị di động hỗ trợ Native Share (iPhone Safari, Android)
  if (navigator.share && /iphone|ipad|ipod|android/i.test(navigator.userAgent)) {
    navigator.share({
      title: document.title,
      url: window.location.href
    }).catch(err => {
      if (err.name !== 'AbortError') {
        window.copyTextToClipboard(window.location.href, 'Đã sao chép liên kết vào bộ nhớ tạm!');
      }
    });
    return;
  }
  window.copyTextToClipboard(window.location.href, 'Đã sao chép liên kết vào bộ nhớ tạm!');
}

/* ==========================================================================
   IMAGE ERROR FALLBACK
   ========================================================================== */
function initImageFallbacks() {
  document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', function() {
      if (!this.src.includes('placeholder.svg')) {
        this.src = '/static/images/placeholder.svg';
      }
    });
  });
}

/* ==========================================================================
   MOBILE FILTER DRAWER (BOTTOM SHEET)
   ========================================================================== */
function initMobileFilterDrawer() {
  const openBtn = document.getElementById('openMobileFilterBtn');
  const closeBtn = document.getElementById('closeMobileFilterBtn');
  const drawer = document.getElementById('mobileFilterDrawer');
  const overlay = document.getElementById('mobileFilterOverlay');

  if (!drawer) return;

  function openDrawer() {
    drawer.classList.add('active');
    if (overlay) overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (openBtn) openBtn.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', closeDrawer);
}

/* ==========================================================================
   TOUCH SWIPE GESTURES FOR MOBILE GALLERY & LIGHTBOX
   ========================================================================== */
function initTouchSwipe() {
  const galleryMain = document.querySelector('.gallery-main');
  const lightboxModal = document.getElementById('lightboxModal');
  const prevBtn = document.getElementById('galleryPrevBtn');
  const nextBtn = document.getElementById('galleryNextBtn');
  const lightboxPrevBtn = document.getElementById('lightboxPrevBtn');
  const lightboxNextBtn = document.getElementById('lightboxNextBtn');

  function attachSwipe(el, onLeft, onRight) {
    if (!el) return;
    let startX = 0;
    let startY = 0;

    el.addEventListener('touchstart', (e) => {
      startX = e.changedTouches[0].screenX;
      startY = e.changedTouches[0].screenY;
    }, { passive: true });

    el.addEventListener('touchend', (e) => {
      const endX = e.changedTouches[0].screenX;
      const endY = e.changedTouches[0].screenY;
      const deltaX = endX - startX;
      const deltaY = endY - startY;

      // Kích hoạt khi vuốt ngang chiếm ưu thế và khoảng cách > 35px
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 35) {
        if (deltaX < 0) {
          if (onLeft) onLeft();
        } else {
          if (onRight) onRight();
        }
      }
    }, { passive: true });
  }

  if (galleryMain) {
    attachSwipe(galleryMain, 
      () => { if (nextBtn) nextBtn.click(); }, 
      () => { if (prevBtn) prevBtn.click(); }
    );
  }

  if (lightboxModal) {
    attachSwipe(lightboxModal, 
      () => { if (lightboxNextBtn) lightboxNextBtn.click(); }, 
      () => { if (lightboxPrevBtn) lightboxPrevBtn.click(); }
    );
  }
}

/* ==========================================================================
   SCROLL TO TOP BUTTON (MOBILE)
   ========================================================================== */
function initScrollToTop() {
  const btn = document.getElementById('btnBackToTop');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      btn.classList.add('show');
    } else {
      btn.classList.remove('show');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ==========================================================================
   AI REWRITE & CLIPBOARD TOOLS
   ========================================================================== */
window.triggerAiRewrite = async function(productId) {
  const btn = document.getElementById('btnAiGenerate');
  const btnText = document.getElementById('btnAiGenerateText');
  const select = document.getElementById('aiAngleSelect');
  const resultCard = document.getElementById('aiResultCard');
  const titleBox = document.getElementById('aiOutputTitle');
  const descBox = document.getElementById('aiOutputDesc');
  const angleBadge = document.getElementById('aiResultAngleBadge');

  if (!btn || !productId) return;

  const chosenAngle = select ? select.value : '';

  // Loading state
  btn.classList.add('loading');
  if (btnText) btnText.textContent = '🤖 AI đang phân tích & viết lại...';
  if (window.showToast) window.showToast('🤖 Đang kết nối Gemini AI để viết bài...');

  try {
    const res = await fetch(`/api/products/${productId}/ai-rewrite`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ angle: chosenAngle })
    });

    const data = await res.json();

    if (res.ok && data.status === 'success') {
      if (titleBox) titleBox.textContent = data.title;
      if (descBox) descBox.textContent = data.description;
      if (angleBadge) angleBadge.textContent = `Phong cách: ${data.angle || chosenAngle}`;
      
      if (resultCard) {
        resultCard.style.display = 'block';
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }

      if (window.showToast) {
        window.showToast('✨ AI đã viết xong bài đăng chuẩn SEO!');
      }
    } else {
      const errMsg = data.message || 'Không thể tạo nội dung từ AI.';
      alert(`Lỗi AI Rewrite: ${errMsg}`);
      if (window.showToast) window.showToast(`❌ ${errMsg}`);
    }
  } catch (err) {
    console.error('AI Rewrite fetch error:', err);
    alert('Không thể kết nối đến máy chủ AI. Vui lòng kiểm tra lại kết nối mạng hoặc API key.');
    if (window.showToast) window.showToast('❌ Lỗi kết nối đến máy chủ AI.');
  } finally {
    btn.classList.remove('loading');
    if (btnText) btnText.textContent = 'Viết Lại Bằng Gemini AI';
  }
};

window.copyAiTitle = function() {
  const box = document.getElementById('aiOutputTitle');
  if (!box) return;
  const text = box.textContent.trim();
  if (text) {
    window.copyTextToClipboard(text, 'Đã sao chép tiêu đề mới!');
  }
};

window.copyAiDesc = function() {
  const box = document.getElementById('aiOutputDesc');
  if (!box) return;
  const text = box.textContent.trim();
  if (text) {
    window.copyTextToClipboard(text, 'Đã sao chép mô tả bài viết!');
  }
};

window.copyAiAll = function() {
  const titleBox = document.getElementById('aiOutputTitle');
  const descBox = document.getElementById('aiOutputDesc');
  const title = titleBox ? titleBox.textContent.trim() : '';
  const desc = descBox ? descBox.textContent.trim() : '';
  const fullText = `${title}\n\n${desc}`.trim();

  if (fullText) {
    window.copyTextToClipboard(fullText, 'Đã sao chép toàn bộ bài viết!');
  }
};

/* ==========================================================================
   TẢI TOÀN BỘ ẢNH TRỰC TIẾP (KHÔNG NÉN ZIP)
   ========================================================================== */
window.downloadAllImagesDirectly = async function() {
  const block = document.getElementById('toolDownloadBlock');
  const btn = document.getElementById('btnDownloadAllImages');
  const btnText = document.getElementById('btnDownloadText');
  const btnIcon = document.getElementById('btnDownloadIcon');

  if (!block || !btn) return;

  const rawImages = block.getAttribute('data-images');
  const productId = block.getAttribute('data-id');
  const productPid = block.getAttribute('data-pid') || 'bds';

  let images = [];
  try {
    images = JSON.parse(rawImages || '[]');
  } catch (e) {
    console.error('Không thể đọc danh sách ảnh:', e);
    images = [];
  }

  if (!images || images.length === 0) {
    alert('Sản phẩm này chưa có hình ảnh để tải về.');
    return;
  }

  const total = images.length;
  const origText = btnText ? btnText.textContent : `Tải Toàn Bộ ${total} Ảnh Về Máy`;

  // Trạng thái đang tải
  btn.disabled = true;
  btn.classList.add('loading');
  if (btnIcon) btnIcon.textContent = '⏳';
  if (window.showToast) window.showToast(`Bắt đầu tải ${total} ảnh trực tiếp về thiết bị...`);

  let successCount = 0;
  const isMobile = /iphone|ipad|ipod|android/i.test(navigator.userAgent);
  const delayMs = isMobile ? 850 : 350;

  for (let i = 0; i < total; i++) {
    const imgItem = images[i];
    if (btnText) {
      btnText.textContent = `Đang tải ảnh ${i + 1}/${total}...`;
    }

    // Xử lý chuẩn xác URL ảnh (nếu đã có tiền tố /images/ thì giữ nguyên, không nối lặp)
    let imgUrl = String(imgItem || '').trim();
    if (!imgUrl.startsWith('/') && !imgUrl.startsWith('http')) {
      imgUrl = `/images/${productId}/${imgUrl}`;
    }

    // Lấy tên file gốc và phần mở rộng chuẩn
    const urlClean = imgUrl.split('?')[0];
    const origFilename = urlClean.substring(urlClean.lastIndexOf('/') + 1) || `anh_${i + 1}.jpg`;
    const ext = origFilename.includes('.') ? origFilename.substring(origFilename.lastIndexOf('.')) : '.jpg';
    const cleanIndex = String(i + 1).padStart(2, '0');
    const cleanFileName = `${productPid}_anh_${cleanIndex}${ext}`;

    try {
      // Tải tệp blob trực tiếp
      const response = await fetch(imgUrl);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} khi tải ảnh`);
      }

      // Kiểm tra kiểu dữ liệu để đảm bảo không lưu nhầm file json/html lỗi
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('json') || contentType.includes('html')) {
        throw new Error(`Server trả về định dạng không phải ảnh: ${contentType}`);
      }

      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = cleanFileName;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Giải phóng URL sau khi đã kích hoạt tải
      setTimeout(() => URL.revokeObjectURL(blobUrl), 15000);
      successCount++;
    } catch (err) {
      console.warn(`Lỗi khi tải blob ảnh ${imgUrl}:`, err);
      // Phương thức dự phòng an toàn: Sử dụng link gốc kèm tham số ?download=1
      try {
        const directUrl = imgUrl.includes('?') ? `${imgUrl}&download=1` : `${imgUrl}?download=1`;
        const link = document.createElement('a');
        link.href = directUrl;
        link.download = cleanFileName;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        successCount++;
      } catch (fallbackErr) {
        console.error('Dự phòng tải ảnh thất bại:', fallbackErr);
      }
    }

    // Khoảng nghỉ giữa các ảnh để trình duyệt không chặn pop-up / spam tải file
    if (i < total - 1) {
      await new Promise(r => setTimeout(r, delayMs));
    }
  }

  // Trạng thái hoàn tất
  btn.classList.remove('loading');
  if (btnIcon) btnIcon.textContent = '✅';
  if (btnText) btnText.textContent = `✓ Đã tải xong ${successCount}/${total} ảnh!`;
  if (window.showToast) {
    window.showToast(`🎉 Đã tải hoàn tất ${successCount} ảnh gốc về thiết bị!`);
  }

  setTimeout(() => {
    btn.disabled = false;
    if (btnIcon) btnIcon.textContent = '📥';
    if (btnText) btnText.textContent = origText;
  }, 3500);
};

