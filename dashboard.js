/**
 * Dashboard JavaScript
 * 테이블 애니메이션 및 인터랙션 처리
 */

(function() {
    'use strict';

    // DOM이 로드되면 실행
    document.addEventListener('DOMContentLoaded', function() {
        initTableAnimations();
    });

    /**
     * 테이블 행 순차 페이드인 애니메이션 초기화
     */
    function initTableAnimations() {
        const tableRows = document.querySelectorAll('.custom-table tbody tr');
        
        if (tableRows.length === 0) return;
        
        // 초기 상태: 모든 행을 숨김
        tableRows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateY(20px)';
            row.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        });
        
        // 순차적으로 나타나기
        tableRows.forEach((row, index) => {
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateY(0)';
            }, index * 50); // 각 행마다 50ms씩 지연
        });
        
        // 숫자 카운트업 애니메이션 적용
        setTimeout(() => {
            initNumberAnimations();
        }, tableRows.length * 50 + 200);
        
        // 호버 효과 설정
        initHoverEffects(tableRows);
    }

    /**
     * 숫자 카운트업 애니메이션 초기화
     */
    function initNumberAnimations() {
        const numberCells = document.querySelectorAll('.number-cell');
        numberCells.forEach((cell, index) => {
            const text = cell.textContent.replace(/[$,]/g, '');
            const value = parseFloat(text);
            
            if (!isNaN(value)) {
                setTimeout(() => {
                    animateNumber(cell, value, 800);
                }, index * 30);
            }
        });
    }

    /**
     * 숫자 카운트업 애니메이션
     * @param {HTMLElement} element - 애니메이션을 적용할 요소
     * @param {number} targetValue - 목표 값
     * @param {number} duration - 애니메이션 지속 시간 (ms)
     */
    function animateNumber(element, targetValue, duration = 1000) {
        const startValue = 0;
        const startTime = performance.now();
        const isCurrency = element.textContent.includes('$');
        const isInteger = !targetValue.toString().includes('.');
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // easing 함수 (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (targetValue - startValue) * easeOut;
            
            if (isCurrency) {
                element.textContent = '$' + currentValue.toFixed(2);
            } else if (isInteger) {
                element.textContent = Math.floor(currentValue).toLocaleString();
            } else {
                element.textContent = currentValue.toFixed(2);
            }
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                // 최종 값 설정
                if (isCurrency) {
                    element.textContent = '$' + targetValue.toFixed(2);
                } else if (isInteger) {
                    element.textContent = Math.floor(targetValue).toLocaleString();
                } else {
                    element.textContent = targetValue.toFixed(2);
                }
            }
        }
        
        requestAnimationFrame(update);
    }

    /**
     * 테이블 행 호버 효과 초기화
     * @param {NodeList} tableRows - 테이블 행 요소들
     */
    function initHoverEffects(tableRows) {
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.01)';
                this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                this.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.boxShadow = 'none';
            });
        });
    }
})();
