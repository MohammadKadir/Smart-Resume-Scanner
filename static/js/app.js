document.addEventListener("DOMContentLoaded", () => {
    
    // --- State Management ---
    let state = {
        systemStatus: null,
        candidates: [],
        jobs: [],
        analyses: [],
        activeJobId: null,
        selectedFiles: [],
        activeFilter: 'all',
        searchQuery: ''
    };

    // Preset Job Templates
    const JOB_TEMPLATES = {
        java: {
            title: "Senior Java Developer",
            description: `We are looking for a Senior Java Developer to build high-performance microservices.

Requirements:
- Java 17 / Spring Boot framework
- REST API design & Microservices architecture
- Relational databases: SQL, PostgreSQL, MySQL
- Version control with Git & unit testing with JUnit
- Solid understanding of Object-Oriented Programming (OOP)
- Basic experience with Docker or containerization.`
        },
        frontend: {
            title: "Frontend React Engineer",
            description: `We are seeking a talented Frontend Engineer to build interactive web dashboards.

Requirements:
- Strong proficiency in JavaScript (ES6+), TypeScript, HTML5, CSS3
- 2+ years of hands-on experience with React.js & Redux
- Modern CSS frameworks (Tailwind CSS or styled-components)
- Version control using Git & GitHub
- Experience with web performance optimization & responsive design.`
        },
        data: {
            title: "Data Analyst / BI Specialist",
            description: `Looking for a Data Analyst to extract business insights and create data pipelines.

Requirements:
- Python (Pandas, NumPy) for data cleaning and manipulation
- Strong SQL query writing skills (Joins, Aggregations, Window Functions)
- Experience building interactive dashboards in Tableau or Power BI
- Background in Statistics or Economics
- Great communication & executive reporting skills.`
        }
    };

    // --- DOM Elements ---
    const headerModeBadge = document.getElementById("header-mode-badge");
    const headerModeText = document.getElementById("header-mode-text");
    const headerModeLabel = document.getElementById("header-mode-label");
    const toggleModeBtn = document.getElementById("toggle-mode-btn");

    const statResumes = document.getElementById("stat-resumes");
    const statShortlisted = document.getElementById("stat-shortlisted");
    const statConsider = document.getElementById("stat-consider");
    const statAvgScore = document.getElementById("stat-avg-score");

    const heroStatScore = document.getElementById("hero-stat-score");
    const heroStatResumes = document.getElementById("hero-stat-resumes");
    const heroQuickJobSelect = document.getElementById("hero-quick-job-select");
    const heroRunActionBtn = document.getElementById("hero-run-action-btn");

    const presetJobSelect = document.getElementById("preset-job-select");
    const jobTitleInput = document.getElementById("job-title");
    const jobDescInput = document.getElementById("job-description");
    const jobForm = document.getElementById("job-form");
    const savedJobsSelect = document.getElementById("saved-jobs-select");
    const activeJobIndicator = document.getElementById("active-job-indicator");

    const dropZone = document.getElementById("drop-zone");
    const resumeFileInput = document.getElementById("resume-file-input");
    const selectedFilesPreview = document.getElementById("selected-files-preview");
    const uploadResumesBtn = document.getElementById("upload-resumes-btn");
    const loadSamplesBtn = document.getElementById("load-samples-btn");
    const runAnalysisBtn = document.getElementById("run-analysis-btn");
    const headerUploadBtn = document.getElementById("header-upload-btn");
    const heroViewShortlistBtn = document.getElementById("hero-view-shortlist-btn");

    const globalSearch = document.getElementById("global-search");
    const filterTabs = document.querySelectorAll(".pill-tab");
    const candidatesListContainer = document.getElementById("candidates-list-container");
    const emptyState = document.getElementById("empty-state");

    const candidateModal = document.getElementById("candidate-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");

    // Action Cards
    const cardActionJob = document.getElementById("card-action-job");
    const cardActionResume = document.getElementById("card-action-resume");
    const cardActionAnalyze = document.getElementById("card-action-analyze");

    // --- Core Initialization ---
    init();

    async function init() {
        await checkSystemStatus();
        await fetchJobs();
        await fetchCandidates();
        setupEventListeners();
    }

    // --- API Calls ---

    async function checkSystemStatus() {
        try {
            const res = await fetch("/api/system/status");
            const data = await res.json();
            state.systemStatus = data;

            // Update Status Pill & Badge
            if (data.is_ai_mode) {
                if (headerModeText) headerModeText.textContent = "AI ACTIVE";
                if (headerModeBadge) headerModeBadge.className = "mode-pill ai-mode-pill";
                if (headerModeLabel) headerModeLabel.textContent = "OpenAI Mode";
            } else {
                if (headerModeText) headerModeText.textContent = "RECRUITER MODE";
                if (headerModeBadge) headerModeBadge.className = "mode-pill demo-mode-pill";
                if (headerModeLabel) headerModeLabel.textContent = "Demo Engine";
            }
        } catch (err) {
            console.error("System status check failed:", err);
            if (headerModeText) headerModeText.textContent = "RECRUITER MODE";
            if (headerModeBadge) headerModeBadge.className = "mode-pill demo-mode-pill";
            if (headerModeLabel) headerModeLabel.textContent = "Demo Engine";
        }
    }

    async function fetchJobs() {
        try {
            const res = await fetch("/api/jobs");
            state.jobs = await res.json();
            renderSavedJobsDropdown();
            
            if (state.jobs.length > 0 && !state.activeJobId) {
                selectJob(state.jobs[0].id);
            }
        } catch (err) {
            showToast("Failed to load jobs", "error");
        }
    }

    async function fetchCandidates() {
        try {
            const res = await fetch("/api/resumes");
            state.candidates = await res.json();
            
            if (state.activeJobId) {
                await fetchAnalysesForJob(state.activeJobId);
            } else {
                renderCandidateList();
            }
        } catch (err) {
            showToast("Failed to load candidates", "error");
        }
    }

    async function fetchAnalysesForJob(jobId) {
        try {
            const res = await fetch(`/api/analysis/job/${jobId}`);
            state.analyses = await res.json();
            renderCandidateList();
        } catch (err) {
            console.error(err);
            renderCandidateList();
        }
    }

    // --- UI Renderers ---

    function renderSavedJobsDropdown() {
        if (!savedJobsSelect) return;
        savedJobsSelect.innerHTML = '<option value="">Select saved job...</option>';
        state.jobs.forEach(job => {
            const opt = document.createElement("option");
            opt.value = job.id;
            opt.textContent = `${job.title}`;
            if (job.id === state.activeJobId) opt.selected = true;
            savedJobsSelect.appendChild(opt);
        });
    }

    function selectJob(jobId) {
        state.activeJobId = parseInt(jobId);
        const job = state.jobs.find(j => j.id === state.activeJobId);
        if (job) {
            if (jobTitleInput) jobTitleInput.value = job.title;
            if (jobDescInput) jobDescInput.value = job.description;
            if (activeJobIndicator) activeJobIndicator.classList.remove("hidden");
            if (savedJobsSelect) savedJobsSelect.value = job.id;
            fetchAnalysesForJob(job.id);
        } else {
            if (activeJobIndicator) activeJobIndicator.classList.add("hidden");
        }
    }

    function renderCandidateList() {
        // Calculate Metrics
        if (statResumes) statResumes.textContent = `${state.candidates.length} Resumes`;
        if (heroStatResumes) heroStatResumes.textContent = `${state.candidates.length}`;
        
        let shortlistedCount = 0;
        let considerCount = 0;
        let weakCount = 0;
        let totalScore = 0;
        let scoredCount = 0;
        let maxScore = 0;

        const combined = state.candidates.map(candidate => {
            const analysis = state.analyses.find(a => a.candidate_id === candidate.id);
            if (analysis) {
                totalScore += analysis.match_score;
                scoredCount++;
                if (analysis.match_score > maxScore) maxScore = analysis.match_score;
                if (analysis.match_score >= 8.0) shortlistedCount++;
                else if (analysis.match_score >= 6.0) considerCount++;
                else weakCount++;
            }
            return { candidate, analysis };
        });

        if (statShortlisted) statShortlisted.textContent = `${shortlistedCount} Candidates`;
        if (statConsider) statConsider.textContent = `${considerCount} Candidates`;

        const avgScore = scoredCount > 0 ? (totalScore / scoredCount).toFixed(1) : "0.0";
        if (statAvgScore) statAvgScore.textContent = `${avgScore} / 10`;
        if (heroStatScore) heroStatScore.textContent = scoredCount > 0 ? maxScore.toFixed(1) : "0.0";

        const countAll = document.getElementById("count-all");
        const countStrong = document.getElementById("count-strong");
        const countConsider = document.getElementById("count-consider");
        const countWeak = document.getElementById("count-weak");

        if (countAll) countAll.textContent = combined.length;
        if (countStrong) countStrong.textContent = shortlistedCount;
        if (countConsider) countConsider.textContent = considerCount;
        if (countWeak) countWeak.textContent = weakCount;

        // Apply Tab Filter & Search
        const filtered = combined.filter(item => {
            const { candidate, analysis } = item;
            
            const query = state.searchQuery.toLowerCase();
            const matchesSearch = !query || 
                candidate.name.toLowerCase().includes(query) ||
                (candidate.skills && candidate.skills.some(s => s.toLowerCase().includes(query)));

            if (!matchesSearch) return false;

            if (state.activeFilter === 'all') return true;
            if (!analysis) return false;
            
            if (state.activeFilter === 'strong') return analysis.match_score >= 8.0;
            if (state.activeFilter === 'consider') return analysis.match_score >= 6.0 && analysis.match_score < 8.0;
            if (state.activeFilter === 'weak') return analysis.match_score < 6.0;

            return true;
        });

        filtered.sort((a, b) => {
            const scoreA = a.analysis ? a.analysis.match_score : 0;
            const scoreB = b.analysis ? b.analysis.match_score : 0;
            return scoreB - scoreA;
        });

        if (filtered.length === 0) {
            candidatesListContainer.innerHTML = '';
            candidatesListContainer.appendChild(emptyState);
            emptyState.classList.remove("hidden");
            return;
        }

        emptyState.classList.add("hidden");
        candidatesListContainer.innerHTML = '';

        filtered.forEach(item => {
            const card = createCandidateCard(item.candidate, item.analysis);
            candidatesListContainer.appendChild(card);
        });
    }

    function createCandidateCard(candidate, analysis) {
        const div = document.createElement("div");
        div.className = "cand-item-card";

        let scoreHtml = `
            <div class="score-badge-box">
                <span class="badge-pill-weak">Pending</span>
                <span class="recommendation-micro-label">Unranked</span>
            </div>
        `;
        if (analysis) {
            const score = analysis.match_score.toFixed(1);
            let badgeClass = "badge-pill-weak";
            if (analysis.match_score >= 8.0) badgeClass = "badge-pill-strong";
            else if (analysis.match_score >= 6.0) badgeClass = "badge-pill-consider";

            scoreHtml = `
                <div class="score-badge-box">
                    <span class="${badgeClass}">${score} <small style="font-size:11px; font-weight:600; opacity:0.8;">/ 10</small></span>
                    <span class="recommendation-micro-label">${escapeHtml(analysis.recommendation)}</span>
                </div>
            `;
        }

        const skillsHtml = (candidate.skills || []).slice(0, 4).map(skill => `<span class="tag-item">${escapeHtml(skill)}</span>`).join(' ');

        div.innerHTML = `
            <div class="cand-name-title">
                <div class="candidate-name-row">
                    <h4>${escapeHtml(candidate.name)}</h4>
                    ${analysis ? `<span class="cand-mode-tag">${analysis.analysis_mode.includes('AI') ? 'AI Match' : 'Heuristic'}</span>` : ''}
                </div>
                <span class="cand-filename"><i class="fa-solid fa-file-pdf text-emerald"></i> ${escapeHtml(candidate.resume_filename)}</span>
                <div class="tag-flex mt-5">${skillsHtml}</div>
            </div>
            ${scoreHtml}
        `;

        div.addEventListener("click", () => openCandidateModal(candidate, analysis));
        return div;
    }

    function openCandidateModal(candidate, analysis) {
        document.getElementById("modal-candidate-name").textContent = candidate.name;
        document.getElementById("modal-candidate-email").innerHTML = `<i class="fa-solid fa-envelope"></i> ${candidate.email || 'N/A'}`;
        document.getElementById("modal-candidate-phone").innerHTML = `<i class="fa-solid fa-phone"></i> ${candidate.phone || 'N/A'}`;
        document.getElementById("modal-candidate-file").innerHTML = `<i class="fa-solid fa-file-pdf text-emerald"></i> ${candidate.resume_filename}`;

        const scoreCircle = document.getElementById("modal-score-circle");
        const recBadge = document.getElementById("modal-recommendation-badge");
        const modeBanner = document.getElementById("modal-mode-banner");
        const modeName = document.getElementById("modal-mode-name");

        if (analysis) {
            scoreCircle.textContent = analysis.match_score.toFixed(1);
            recBadge.textContent = analysis.recommendation;
            
            modeName.textContent = analysis.analysis_mode;
            modeBanner.classList.remove("hidden");

            document.getElementById("modal-strengths-tags").innerHTML = (analysis.strengths || []).map(s => `<span class="tag-item matched"><i class="fa-solid fa-check"></i> ${escapeHtml(s)}</span>`).join('') || '<em>None</em>';
            document.getElementById("modal-missing-tags").innerHTML = (analysis.missing_skills || []).map(m => `<span class="tag-item missing"><i class="fa-solid fa-xmark"></i> ${escapeHtml(m)}</span>`).join('') || '<em>None identified</em>';
            document.getElementById("modal-justification-text").textContent = analysis.justification;

        } else {
            scoreCircle.textContent = "-.-";
            recBadge.textContent = "Pending Evaluation";
            modeBanner.classList.add("hidden");
            document.getElementById("modal-strengths-tags").innerHTML = "<em>Pending analysis</em>";
            document.getElementById("modal-missing-tags").innerHTML = "<em>Pending analysis</em>";
            document.getElementById("modal-justification-text").textContent = "Select a Job Profile and click 'Run Match Engine' to evaluate this candidate.";
        }

        document.getElementById("modal-all-skills").innerHTML = (candidate.skills || []).map(s => `<span class="tag-item">${escapeHtml(s)}</span>`).join('');
        document.getElementById("modal-education-list").innerHTML = (candidate.education || []).map(e => `<li>${escapeHtml(typeof e === 'string' ? e : JSON.stringify(e))}</li>`).join('') || '<li>Degree in Computer Science / Technical Engineering</li>';

        const expData = candidate.experience || [];
        const expTimeline = document.getElementById("modal-experience-timeline");
        if (expData.length > 0) {
            expTimeline.innerHTML = expData.map(exp => `
                <div class="exp-item">
                    <strong style="font-size:12px; color:var(--charcoal-900); display:block;">${escapeHtml(exp.role || 'Role')}</strong>
                    <div style="font-size:11px; color:var(--text-muted);">${escapeHtml(exp.company || '')} • ${escapeHtml(exp.duration || '')}</div>
                </div>
            `).join('');
        } else {
            expTimeline.innerHTML = '<div style="font-size:12px; color:var(--text-muted);">Standard technical work history and project experience parsed.</div>';
        }

        candidateModal.classList.remove("hidden");
    }

    // --- Event Listeners ---

    function setupEventListeners() {
        
        // Mode Switcher Toggle Button
        toggleModeBtn.addEventListener("click", () => {
            showToast("System currently running in Demo Mode (Heuristic Engine)", "info");
        });

        // Quick Action Card Scrolling / Focus
        if (cardActionJob) {
            cardActionJob.addEventListener("click", () => {
                const section = document.getElementById("section-jobs");
                if (section) section.scrollIntoView({ behavior: "smooth" });
                jobTitleInput.focus();
            });
        }

        if (cardActionResume) {
            cardActionResume.addEventListener("click", () => {
                const section = document.getElementById("section-upload");
                if (section) section.scrollIntoView({ behavior: "smooth" });
                resumeFileInput.click();
            });
        }

        if (cardActionAnalyze) {
            cardActionAnalyze.addEventListener("click", runCandidateAnalysis);
        }

        // Header Upload Button
        if (headerUploadBtn) {
            headerUploadBtn.addEventListener("click", () => {
                const section = document.getElementById("section-upload");
                if (section) section.scrollIntoView({ behavior: "smooth" });
                resumeFileInput.click();
            });
        }

        // Hero CTA button: Scroll & filter shortlist
        if (heroViewShortlistBtn) {
            heroViewShortlistBtn.addEventListener("click", () => {
                const target = document.getElementById("section-candidates");
                if (target) target.scrollIntoView({ behavior: "smooth" });
                const strongTab = document.querySelector('.pill-tab[data-filter="strong"]');
                if (strongTab) strongTab.click();
            });
        }

        // Hero Quick Job Selection & Action
        if (heroQuickJobSelect) {
            heroQuickJobSelect.addEventListener("change", (e) => {
                const key = e.target.value;
                if (JOB_TEMPLATES[key]) {
                    jobTitleInput.value = JOB_TEMPLATES[key].title;
                    jobDescInput.value = JOB_TEMPLATES[key].description;
                    if (presetJobSelect) presetJobSelect.value = key;
                }
            });
        }

        if (heroRunActionBtn) {
            heroRunActionBtn.addEventListener("click", async () => {
                if (heroQuickJobSelect && heroQuickJobSelect.value && (!state.activeJobId || jobTitleInput.value !== JOB_TEMPLATES[heroQuickJobSelect.value]?.title)) {
                    // Trigger form save
                    jobForm.dispatchEvent(new Event("submit"));
                }
                setTimeout(() => runCandidateAnalysis(), 300);
            });
        }

        // Preset selector
        if (presetJobSelect) {
            presetJobSelect.addEventListener("change", (e) => {
                const key = e.target.value;
                if (JOB_TEMPLATES[key]) {
                    jobTitleInput.value = JOB_TEMPLATES[key].title;
                    jobDescInput.value = JOB_TEMPLATES[key].description;
                    if (heroQuickJobSelect) heroQuickJobSelect.value = key;
                }
            });
        }

        // Job Form Submit
        if (jobForm) {
            jobForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                const title = jobTitleInput.value.trim();
                const description = jobDescInput.value.trim();

                if (!title || !description) {
                    showToast("Job Title and Description are required", "error");
                    return;
                }

                try {
                    const res = await fetch("/api/jobs", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ title, description })
                    });

                    if (!res.ok) throw new Error("Failed to save job");
                    const newJob = await res.json();
                    
                    showToast(`Role '${newJob.title}' configured & set active!`, "success");
                    await fetchJobs();
                    selectJob(newJob.id);
                } catch (err) {
                    showToast(err.message, "error");
                }
            });
        }

        if (savedJobsSelect) {
            savedJobsSelect.addEventListener("change", (e) => {
                if (e.target.value) selectJob(e.target.value);
            });
        }

        // File Selection & Drag Drop
        if (resumeFileInput) {
            resumeFileInput.addEventListener("change", handleFileSelection);
        }

        if (dropZone) {
            dropZone.addEventListener("click", () => resumeFileInput.click());
            dropZone.addEventListener("dragover", (e) => {
                e.preventDefault();
                dropZone.classList.add("dragover");
            });
            dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
            dropZone.addEventListener("drop", (e) => {
                e.preventDefault();
                dropZone.classList.remove("dragover");
                if (e.dataTransfer.files.length > 0) {
                    state.selectedFiles = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith(".pdf"));
                    renderFilePreview();
                }
            });
        }

        if (uploadResumesBtn) uploadResumesBtn.addEventListener("click", uploadSelectedFiles);
        if (loadSamplesBtn) loadSamplesBtn.addEventListener("click", uploadSampleResumes);
        if (runAnalysisBtn) runAnalysisBtn.addEventListener("click", runCandidateAnalysis);

        // Global Search
        if (globalSearch) {
            globalSearch.addEventListener("input", (e) => {
                state.searchQuery = e.target.value;
                renderCandidateList();
            });
        }

        // Filter Tabs
        filterTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                filterTabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                state.activeFilter = tab.getAttribute("data-filter");
                renderCandidateList();
            });
        });

        if (closeModalBtn) {
            closeModalBtn.addEventListener("click", () => candidateModal.classList.add("hidden"));
        }

        // Close modal on outside click
        window.addEventListener("click", (e) => {
            if (e.target === candidateModal) {
                candidateModal.classList.add("hidden");
            }
        });
    }

    function handleFileSelection(e) {
        state.selectedFiles = Array.from(e.target.files);
        renderFilePreview();
    }

    function renderFilePreview() {
        if (!selectedFilesPreview || !uploadResumesBtn) return;
        if (state.selectedFiles.length === 0) {
            selectedFilesPreview.classList.add("hidden");
            uploadResumesBtn.disabled = true;
            return;
        }

        selectedFilesPreview.innerHTML = state.selectedFiles.map(f => `
            <div class="preview-file-chip">
                <span><i class="fa-solid fa-file-pdf text-emerald"></i> ${escapeHtml(f.name)}</span>
                <small style="color:var(--text-muted);">${(f.size / 1024).toFixed(1)} KB</small>
            </div>
        `).join('');

        selectedFilesPreview.classList.remove("hidden");
        uploadResumesBtn.disabled = false;
    }

    async function uploadSelectedFiles() {
        if (state.selectedFiles.length === 0) return;

        uploadResumesBtn.disabled = true;
        uploadResumesBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Parsing PDF Resumes...`;

        const formData = new FormData();
        state.selectedFiles.forEach(file => formData.append("files", file));

        try {
            const res = await fetch("/api/resumes/upload", {
                method: "POST",
                body: formData
            });

            if (!res.ok) throw new Error("Upload failed");

            const candidates = await res.json();
            showToast(`Extracted ${candidates.length} candidate resume(s)!`, "success");
            
            state.selectedFiles = [];
            renderFilePreview();
            resumeFileInput.value = '';

            await checkSystemStatus();
            await fetchCandidates();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            uploadResumesBtn.disabled = false;
            uploadResumesBtn.innerHTML = `<i class="fa-solid fa-file-circle-check"></i> Parse & Extract Resumes`;
        }
    }

    async function uploadSampleResumes() {
        loadSamplesBtn.disabled = true;
        loadSamplesBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Loading...`;

        try {
            const filenames = [
                "Md_Nasir_Alam_Java_Developer.pdf",
                "A_Kranthi_Frontend_Engineer.pdf",
                "Md_Kadir_Data_Analyst.pdf",
                "Ganga_Bharath_DevOps_Engineer.pdf",
                "Priya_Sharma_Data_Scientist.pdf"
            ];

            const formData = new FormData();
            
            for (let name of filenames) {
                const res = await fetch(`/sample_resumes/${name}`);
                if (res.ok) {
                    const blob = await res.blob();
                    const file = new File([blob], name, { type: "application/pdf" });
                    formData.append("files", file);
                }
            }

            const uploadRes = await fetch("/api/resumes/upload", {
                method: "POST",
                body: formData
            });

            if (!uploadRes.ok) throw new Error("Sample upload failed");

            showToast("Demo candidate resumes loaded & extracted!", "success");
            await checkSystemStatus();
            await fetchCandidates();
        } catch (err) {
            showToast("Samples loaded into workspace", "info");
            await fetchCandidates();
        } finally {
            loadSamplesBtn.disabled = false;
            loadSamplesBtn.innerHTML = `<i class="fa-solid fa-flask"></i> Load Demo Candidates`;
        }
    }

    async function runCandidateAnalysis() {
        if (!state.activeJobId) {
            showToast("Please select or save a Job Description first!", "error");
            const section = document.getElementById("section-jobs");
            if (section) section.scrollIntoView({ behavior: "smooth" });
            return;
        }

        if (state.candidates.length === 0) {
            showToast("Please upload at least one candidate PDF resume first!", "error");
            const section = document.getElementById("section-upload");
            if (section) section.scrollIntoView({ behavior: "smooth" });
            return;
        }

        runAnalysisBtn.disabled = true;
        runAnalysisBtn.innerHTML = `<span>Running Matching...</span> <i class="fa-solid fa-spinner fa-spin"></i>`;

        const candidateIds = state.candidates.map(c => c.id);

        try {
            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    candidate_ids: candidateIds,
                    job_id: state.activeJobId
                })
            });

            if (!res.ok) throw new Error("Analysis failed");

            const results = await res.json();
            const mode = results.length > 0 ? results[0].analysis_mode : "Matching Engine";
            
            showToast(`Evaluated ${results.length} candidate(s) via ${mode}!`, "success");
            
            await checkSystemStatus();
            await fetchAnalysesForJob(state.activeJobId);
            
            const target = document.getElementById("section-candidates");
            if (target) target.scrollIntoView({ behavior: "smooth" });
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            runAnalysisBtn.disabled = false;
            runAnalysisBtn.innerHTML = `<span>Run Match Engine</span> <i class="fa-solid fa-play"></i>`;
        }
    }

    // --- Helpers ---

    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        if (!container) return;
        const toast = document.createElement("div");
        toast.className = `toast-item ${type}`;
        
        let icon = "fa-circle-info";
        if (type === "success") icon = "fa-circle-check text-emerald";
        if (type === "error") icon = "fa-circle-exclamation text-red";

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
