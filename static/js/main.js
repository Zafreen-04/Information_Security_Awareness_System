/**
 * Information Security Awareness Measurement System
 * Client-Side Interactivity, Validation, and Filtering
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Dynamic Respondent Type and Age Validation
    const respondentTypeSelect = document.getElementById('respondent_type');
    const ageInput = document.getElementById('age');
    const ageHint = document.getElementById('age_hint');

    if (respondentTypeSelect && ageInput) {
        function updateAgeConstraints() {
            const selectedType = respondentTypeSelect.value;
            if (selectedType === 'Student') {
                ageInput.min = 12;
                ageInput.max = 19;
                ageInput.placeholder = "Age (12 - 19)";
                if (ageHint) ageHint.textContent = "Recommended high school age: 12 to 19 years.";
            } else if (selectedType === 'Teacher') {
                ageInput.min = 20;
                ageInput.max = 80;
                ageInput.placeholder = "Age (20 - 80)";
                if (ageHint) ageHint.textContent = "Faculty/Adult educator age: 20 to 80 years.";
            } else {
                ageInput.removeAttribute('min');
                ageInput.removeAttribute('max');
                if (ageHint) ageHint.textContent = "";
            }
        }

        respondentTypeSelect.addEventListener('change', updateAgeConstraints);
        // Initial setup
        updateAgeConstraints();
    }

    // 2. Questionnaire Completion Tracker & Form Validation
    const questionnaireForm = document.getElementById('questionnaire-form');
    if (questionnaireForm) {
        const questionCodes = ['ISBP1', 'ISBP2', 'ISBP3', 'ISBS1', 'ISBS2', 'ISBS3', 'ISBE1', 'ISBE2', 'ISBE3'];
        const progressBadge = document.getElementById('answered-count-badge');
        const progressBar = document.getElementById('questionnaire-progress-bar');

        function updateProgress() {
            let answered = 0;
            questionCodes.forEach(code => {
                const checked = questionnaireForm.querySelector(`input[name="${code}"]:checked`);
                if (checked) answered++;
            });

            if (progressBadge) {
                progressBadge.textContent = `${answered} / 9 Answered`;
            }
            if (progressBar) {
                const pct = Math.round((answered / 9) * 100);
                progressBar.style.width = `${pct}%`;
                progressBar.setAttribute('aria-valuenow', pct);
            }
        }

        // Attach change listeners to all radios
        questionCodes.forEach(code => {
            const radios = questionnaireForm.querySelectorAll(`input[name="${code}"]`);
            radios.forEach(radio => radio.addEventListener('change', updateProgress));
        });

        // Form submit handler
        questionnaireForm.addEventListener('submit', function (e) {
            let unanswered = [];
            questionCodes.forEach(code => {
                const checked = questionnaireForm.querySelector(`input[name="${code}"]:checked`);
                if (!checked) {
                    unanswered.push(code);
                }
            });

            if (unanswered.length > 0) {
                e.preventDefault();
                alert(`Please answer all mandatory questions. Unanswered items: ${unanswered.join(', ')}`);
                // Scroll to first unanswered item
                const firstUnanswered = questionnaireForm.querySelector(`[name="${unanswered[0]}"]`);
                if (firstUnanswered) {
                    firstUnanswered.closest('.likert-container').scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return false;
            }

            // Age validation check
            if (ageInput && respondentTypeSelect) {
                const ageVal = parseInt(ageInput.value, 10);
                const typeVal = respondentTypeSelect.value;
                if (typeVal === 'Student' && (ageVal < 12 || ageVal > 19)) {
                    e.preventDefault();
                    alert("Please enter a valid student age between 12 and 19 years.");
                    ageInput.focus();
                    return false;
                }
                if (typeVal === 'Teacher' && (ageVal < 20 || ageVal > 80)) {
                    e.preventDefault();
                    alert("Please enter a valid teacher age between 20 and 80 years.");
                    ageInput.focus();
                    return false;
                }
            }
        });

        // Initial progress update
        updateProgress();
    }

    // 3. Client-Side Respondents Table Filter & Search
    const searchInput = document.getElementById('table-search-input');
    const filterType = document.getElementById('filter-type-select');
    const filterLevel = document.getElementById('filter-level-select');
    const respondentsTable = document.getElementById('respondents-table');

    if (respondentsTable && (searchInput || filterType || filterLevel)) {
        function filterTable() {
            const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
            const typeFilter = filterType ? filterType.value : '';
            const levelFilter = filterLevel ? filterLevel.value : '';

            const rows = respondentsTable.querySelectorAll('tbody tr');
            let visibleCount = 0;

            rows.forEach(row => {
                const nameText = row.getAttribute('data-name') || '';
                const schoolText = row.getAttribute('data-school') || '';
                const rowType = row.getAttribute('data-type') || '';
                const rowLevel = row.getAttribute('data-level') || '';

                const matchesSearch = !query || nameText.toLowerCase().includes(query) || schoolText.toLowerCase().includes(query);
                const matchesType = !typeFilter || rowType === typeFilter;
                const matchesLevel = !levelFilter || rowLevel === levelFilter;

                if (matchesSearch && matchesType && matchesLevel) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            const countDisplay = document.getElementById('filtered-count-display');
            if (countDisplay) {
                countDisplay.textContent = `Showing ${visibleCount} record(s)`;
            }
        }

        if (searchInput) searchInput.addEventListener('input', filterTable);
        if (filterType) filterType.addEventListener('change', filterTable);
        if (filterLevel) filterLevel.addEventListener('change', filterTable);
    }
});
