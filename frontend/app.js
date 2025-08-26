// Smart Payment Engine
class Switcher {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.initializeAnimations();
        this.loadExampleQueries();
    }

    initializeElements() {
        this.queryInput = document.getElementById('queryInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.pipeline = document.getElementById('aiPipeline');
        this.results = document.getElementById('results');
        this.exampleChips = document.querySelectorAll('.example-chip');
        this.pipelineStages = document.querySelectorAll('.pipeline-stage');
        this.progressFill = document.querySelector('.progress-fill');
        // Demo UI
        this.demoModeCheckbox = document.getElementById('demoMode');
        this.demoSection = document.getElementById('demoSection');
        this.demoButtons = document.querySelectorAll('.demo-btn');
        this.demoScenarios = {
            coffee: "$5.50 at Peet's Coffee",
            grocery: "grocery shopping $120 at Whole Foods",
            travel: "planning $2000 Europe trip next month",
            gas: "filling up gas $45 at Shell station"
        };
    }

    attachEventListeners() {
        if (this.analyzeBtn) {
            this.analyzeBtn.addEventListener('click', () => {
                this.analyzeTransaction();
            });
        } else {
            console.error('Analyze button not found');
        }
        
        if (this.queryInput) {
            this.queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeTransaction();
                }
            });
        }
        
        this.exampleChips.forEach(chip => {
            chip.addEventListener('click', (e) => {
                this.queryInput.value = e.target.textContent;
                this.queryInput.focus();
            });
        });

        // Demo toggle
        if (this.demoModeCheckbox) {
            this.demoModeCheckbox.addEventListener('change', () => {
                if (this.demoSection) {
                    this.demoSection.classList.toggle('active', this.demoModeCheckbox.checked);
                }
                try {
                    localStorage.setItem('demoMode', this.demoModeCheckbox.checked ? '1' : '0');
                } catch (e) {
                    // ignore storage errors
                }
            });
            // Initialize demo mode state on load: default ON if no preference saved
            try {
                const saved = localStorage.getItem('demoMode');
                const enabled = saved ? saved === '1' : true;
                this.demoModeCheckbox.checked = enabled;
                if (this.demoSection) {
                    this.demoSection.classList.toggle('active', enabled);
                }
            } catch (e) {
                // Fallback to enabling by default
                this.demoModeCheckbox.checked = true;
                if (this.demoSection) {
                    this.demoSection.classList.add('active');
                }
            }
        }

        // Demo buttons
        if (this.demoButtons && this.demoButtons.length) {
            this.demoButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    const scenario = btn.dataset.scenario;
                    this.runDemo(scenario);
                });
            });
        }
    }

    initializeAnimations() {
        // Add staggered animation to metric cards on load
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('slide-in');
                    }, index * 100);
                }
            });
        });

        document.querySelectorAll('.metric-card').forEach(card => {
            observer.observe(card);
        });
    }

    loadExampleQueries() {
        const examples = [
            "I spend $200/month on gas",
            "Coffee at Peet's Coffee daily for $5",
            "Netflix subscription $15.99/month",
            "Groceries at Whole Foods $400/month",
            "Dining out $300 monthly"
        ];
        
        const container = document.querySelector('.example-queries');
        if (container && container.children.length === 0) {
            const label = document.createElement('span');
            label.className = 'example-label';
            label.textContent = 'Try these:';
            container.appendChild(label);
            
            examples.forEach(example => {
                const chip = document.createElement('div');
                chip.className = 'example-chip';
                chip.textContent = example;
                chip.addEventListener('click', () => {
                    this.queryInput.value = example;
                    this.queryInput.focus();
                });
                container.appendChild(chip);
            });
        }
    }

    async analyzeTransaction() {
        const query = this.queryInput.value.trim();
        
        if (!query) {
            alert('Please enter a transaction description');
            return;
        }
        
        // Prepare UI for new analysis
        this.resetUIForNewAnalysis();
        // Call fetchOptimization which handles everything
        this.fetchOptimization(query);
    }

    showPipeline() {
        const pipeline = document.getElementById('aiPipeline');
        if (pipeline) {
            pipeline.classList.add('active');
        }
    }
    
    hidePipeline() {
        const pipeline = document.getElementById('aiPipeline');
        if (pipeline) {
            pipeline.classList.remove('active');
        }
    }
    
    updatePipelineStage(stageName, status) {
        const stage = document.querySelector(`[data-stage="${stageName}"]`);
        if (stage) {
            stage.classList.remove('active', 'completed');
            if (status === 'active') {
                stage.classList.add('active');
            } else if (status === 'completed') {
                stage.classList.add('completed');
            }
        }
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    capitalize(str) {
        if (!str || typeof str !== 'string') return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    // Baseline and frequency helpers
    getBaselineRate() {
        // Switch baseline to 2%
        return 0.02;
    }
    
    getFrequencyPresetForCategory(categoryRaw) {
        const category = (categoryRaw || '').toLowerCase();
        // defaults
        let value = 1, period = 'per_month';
        if (category.includes('coffee') || category.includes('cafe')) {
            value = 4; period = 'per_week';
        } else if (category.includes('dining') || category.includes('restaurant')) {
            value = 2; period = 'per_week';
        } else if (category.includes('grocery')) {
            value = 6; period = 'per_month';
        } else if (category.includes('gas') || category.includes('fuel')) {
            value = 4; period = 'per_month';
        } else if (category.includes('transit') || category.includes('commute')) {
            value = 5; period = 'per_week';
        } else if (category.includes('subscription') || category.includes('stream')) {
            value = 1; period = 'per_month';
        } else if (category.includes('utility')) {
            value = 1; period = 'per_month';
        } else if (category.includes('travel') || category.includes('flight') || category.includes('airfare')) {
            value = 1; period = 'per_year'; // trips/year handled via label
        } else if (category.includes('hotel') || category.includes('lodging')) {
            value = 5; period = 'per_year';
        } else if (category.includes('electronics') || category.includes('retail')) {
            value = 2; period = 'per_year';
        }
        return { value, period };
    }
    
    loadFrequencyPref(categoryRaw) {
        try {
            const key = 'switcher_freq_prefs';
            const store = JSON.parse(localStorage.getItem(key) || '{}');
            const cat = (categoryRaw || 'general').toLowerCase();
            return store[cat] || null;
        } catch (_) { return null; }
    }
    
    saveFrequencyPref(categoryRaw, value, period) {
        try {
            const key = 'switcher_freq_prefs';
            const store = JSON.parse(localStorage.getItem(key) || '{}');
            const cat = (categoryRaw || 'general').toLowerCase();
            store[cat] = { value, period };
            localStorage.setItem(key, JSON.stringify(store));
        } catch (_) { /* noop */ }
    }
    
    periodFactor(period) {
        switch (period) {
            case 'per_week': return 52;
            case 'per_month': return 12;
            case 'per_year': return 1;
            case 'per_trip': return 1;
            default: return 12;
        }
    }
    
    formatFrequencyLabel(period, categoryRaw) {
        // Used in assumption copy
        const category = (categoryRaw || '').toLowerCase();
        if (period === 'per_trip' || category.includes('travel') || category.includes('flight')) return 'trips per year';
        if (period === 'per_week') return 'per week';
        if (period === 'per_month') return 'per month';
        return 'per year';
    }
    
    resetUIForNewAnalysis() {
        // Clear results and hide
        if (this.results) {
            this.results.innerHTML = '';
            this.results.classList.remove('active');
        }
        // Show pipeline container
        if (this.pipeline) {
            this.pipeline.classList.add('active');
        }
        // Reset stages and progress bar
        if (this.pipelineStages && this.pipelineStages.length) {
            this.pipelineStages.forEach(stage => stage.classList.remove('active', 'completed', 'complete'));
        }
        if (this.progressFill) {
            this.progressFill.style.width = '0%';
        }
    }
    
    async fetchOptimization(query) {
        try {
            this.showPipeline();
            this.updatePipelineStage('parse', 'active');
            if (this.progressFill) this.progressFill.style.width = '10%';
            if (this.analyzeBtn) {
                this.analyzeBtn.disabled = true;
                this.analyzeBtn.textContent = 'Analyzing...';
            }
            
            // Abort fetch if it takes too long to avoid indefinite 'running' state
            const controller = new AbortController();
            const timeoutMs = 15000; // 15s overall timeout
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            
            const response = await fetch('/api/optimize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query }),
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            clearTimeout(timeoutId);
            const data = await response.json();
            
            // Update pipeline stages with progress animation
            this.updatePipelineStage('parse', 'completed');
            this.updatePipelineStage('research', 'active');
            if (this.progressFill) this.progressFill.style.width = '40%';
            await this.sleep(500);
            this.updatePipelineStage('research', 'completed');
            this.updatePipelineStage('analyze', 'active');
            if (this.progressFill) this.progressFill.style.width = '70%';
            await this.sleep(500);
            this.updatePipelineStage('analyze', 'completed');
            this.updatePipelineStage('recommend', 'active');
            if (this.progressFill) this.progressFill.style.width = '90%';
            await this.sleep(500);
            this.updatePipelineStage('recommend', 'completed');
            if (this.progressFill) this.progressFill.style.width = '100%';
            
            // Hide pipeline and show results
            setTimeout(() => {
                this.hidePipeline();
                // Render using premium layout
                this.renderRecommendations(data);
            }, 1000);
            
        } catch (error) {
            console.error('Error fetching optimization:', error);
            this.hidePipeline();
            if (error.name === 'AbortError') {
                this.showError('The analysis took too long and was canceled. Please try again.');
            } else {
                this.showError('Failed to analyze transaction. Please try again.');
            }
        } finally {
            if (this.analyzeBtn) {
                this.analyzeBtn.disabled = false;
                this.analyzeBtn.textContent = 'Analyze Transaction';
            }
        }
    }

    startAnalysis() {
        this.pipeline.classList.add('active');
        this.results.classList.remove('active');
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Analyzing...';
        
        this.animatePipeline();
    }

    animatePipeline() {
        const stages = ['parse', 'research', 'analyze', 'recommend'];
        let currentStage = 0;
        
        const animateStage = () => {
            if (currentStage > 0) {
                this.pipelineStages[currentStage - 1].classList.remove('active');
                this.pipelineStages[currentStage - 1].classList.add('completed');
            }
            
            if (currentStage < stages.length) {
                this.pipelineStages[currentStage].classList.add('active');
                const progress = ((currentStage + 1) / stages.length) * 100;
                this.progressFill.style.width = `${progress}%`;
                currentStage++;
                setTimeout(animateStage, 800);
            }
        };
        
        // Reset stages
        this.pipelineStages.forEach(stage => {
            stage.classList.remove('active', 'completed');
        });
        this.progressFill.style.width = '0%';
        
        setTimeout(animateStage, 300);
    }

    completeAnalysis() {
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.textContent = 'Analyze Transaction';
        
        setTimeout(() => {
            this.pipeline.classList.remove('active');
        }, 1000);
    }

    displayResults(data) {
        this.results.innerHTML = '';
        this.results.classList.add('active');

        // Display metrics
        const metricsHtml = this.createMetricsSection(data);
        
        // Display transaction details
        const transactionHtml = this.createTransactionSection(data);
        
        // Display recommendations
        const recommendationsHtml = this.createRecommendationsSection(data);
        
        // Display financial impact
        const impactHtml = this.createImpactSection(data);
        
        // Display source attribution
        const sourceHtml = this.createSourceSection(data);

        this.results.innerHTML = `
            ${metricsHtml}
            ${transactionHtml}
            ${recommendationsHtml}
            ${impactHtml}
            ${sourceHtml}
        `;

        // Animate elements
        this.animateResults();
    }

    createMetricsSection(data) {
        const transaction = data.parsed_transaction || data.transaction || {};
        const recommendation = data.recommendation || {};
        const impact = data.financial_impact || {};
        // Derive a safe display for reward rate if only dollar value is provided
        const best = recommendation.best_overall || {};
        const amt = Number(transaction.amount || 0);
        const bestDollar = Number(best.reward_amount || best.reward_value || 0);
        const bestRateDisplay = best.reward_rate || (amt > 0 && bestDollar > 0 ? `${((bestDollar / amt) * 100).toFixed(1)}% cash back` : '—');
        
        return `
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Transaction Amount</div>
                    <div class="metric-value">$${transaction.amount || 0}</div>
                    <div class="metric-change">${transaction.category || 'General'}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Best Reward Rate</div>
                    <div class="metric-value positive">${bestRateDisplay}</div>
                    <div class="metric-change">Cash back</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Annual Savings</div>
                    <div class="metric-value positive">$${impact.annual_projection ? parseFloat(impact.annual_projection.match(/\d+(\.\d+)?/)?.[0] || 0).toFixed(2) : (recommendation.best_overall?.reward_amount || 0) * 365}</div>
                    <div class="metric-change">Potential earnings</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">AI Confidence</div>
                    <div class="metric-value">${this.calculateConfidence(data)}%</div>
                    <div class="metric-change">Analysis accuracy</div>
                </div>
            </div>
        `;
    }

    createTransactionSection(data) {
        const transaction = data.parsed_transaction || data.transaction || {};
        
        return `
            <div class="transaction-card">
                <div class="transaction-header">
                    <div class="transaction-title">Transaction Analysis</div>
                    <div class="confidence-badge">
                        <span class="confidence-value">${this.calculateConfidence(data)}% Confidence</span>
                    </div>
                </div>
                <div class="transaction-details">
                    <div class="detail-item">
                        <div class="detail-label">Merchant</div>
                        <div class="detail-value">${transaction.merchant || 'Unknown'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Category</div>
                        <div class="detail-value">${this.capitalize(transaction.category || 'General')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Amount</div>
                        <div class="detail-value">$${transaction.amount || 0}</div>
                    </div>
                </div>
            </div>
        `;
    }

    createRecommendationsSection(data) {
        const recommendation = data.recommendation || {};
        const cards = [];
        
        if (recommendation.best_overall) {
            cards.push(this.createCardElement(recommendation.best_overall, true));
        }
        if (recommendation.runner_up) {
            cards.push(this.createCardElement(recommendation.runner_up, false));
        }
        if (recommendation.alternative) {
            cards.push(this.createCardElement(recommendation.alternative, false));
        }
        
        if (cards.length === 0) {
            return '<div class="no-recommendations">No recommendations available</div>';
        }
        
        return `
            <div class="recommendations-section">
                <div class="section-header">
                    <div class="section-title">Recommended Cards</div>
                    <div class="section-subtitle">Based on your spending pattern</div>
                </div>
                <div class="cards-container">
                    ${cards.join('')}
                </div>
            </div>
        `;
    }

    createCardElement(card, isBest = false) {
        const name = card.name || card.card_name || 'Unknown Card';
        const rewardAmount = card.reward_amount || card.reward_value || 0;
        const rewardRate = card.reward_rate || `${rewardAmount}% cash back`;
        const fee = card.annual_fee || 0;
        const netValue = card.net_value || rewardAmount;
        
        return `
            <div class="card-recommendation ${isBest ? 'best' : ''}">
                <div class="card-header">
                    <div class="card-info">
                        <div class="card-name">${name}</div>
                        <div class="card-issuer">${card.issuer || 'Bank'}</div>
                    </div>
                    <div class="reward-display">
                        <div class="reward-amount">+$${typeof rewardAmount === 'number' ? rewardAmount.toFixed(2) : rewardAmount}</div>
                        <div class="reward-label">${rewardRate}</div>
                    </div>
                </div>
                <div class="card-features">
                    <div class="feature-item">
                        <div class="feature-icon">$</div>
                        <div class="feature-text">Annual Fee: $${fee}</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">✓</div>
                        <div class="feature-text">Net Value: $${netValue.toFixed(2)}</div>
                    </div>
                    ${card.bonus ? `
                    <div class="feature-item">
                        <div class="feature-icon">★</div>
                        <div class="feature-text">${card.bonus}</div>
                    </div>
                    ` : ''}
                    ${card.additional_benefits ? `
                    <div class="feature-item">
                        <div class="feature-icon">+</div>
                        <div class="feature-text">${card.additional_benefits}</div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createImpactSection(data) {
        const impact = data.financial_impact || {};
        const recommendation = data.recommendation || {};
        const transaction = data.parsed_transaction || data.transaction || {};
        
        // Calculate annual savings from recommendation data
        let annualSavings = 0;
        if (impact.annual_projection) {
            // Extract number from string like "Could earn $120/year"
            const match = impact.annual_projection.match(/\$?([\d.]+)/);  
            annualSavings = match ? parseFloat(match[1]) : 0;
        } else if (recommendation.best_overall?.reward_amount) {
            // Calculate based on transaction frequency
            const rewardPerTransaction = recommendation.best_overall.reward_amount;
            if (transaction.frequency?.includes('monthly')) {
                annualSavings = rewardPerTransaction * 12;
            } else if (transaction.frequency?.includes('daily')) {
                annualSavings = rewardPerTransaction * 365;
            } else if (transaction.frequency?.includes('weekly')) {
                annualSavings = rewardPerTransaction * 52;
            } else {
                annualSavings = rewardPerTransaction;
            }
        }
        
        const monthlySavings = annualSavings / 12;
        const opportunityCost = impact.opportunity_cost ? parseFloat(impact.opportunity_cost.match(/\$?([\d.]+)/)?.[1] || 0) : 0;
        
        return `
            <div class="impact-section">
                <div class="impact-header">
                    <div class="impact-title">Financial Impact</div>
                    <div class="impact-amount">+$${annualSavings.toFixed(2)}</div>
                    <div class="impact-period">Estimated Annual Savings</div>
                </div>
                <div class="impact-breakdown">
                    <div class="breakdown-item">
                        <div class="breakdown-value">$${monthlySavings.toFixed(2)}</div>
                        <div class="breakdown-label">Monthly</div>
                    </div>
                    <div class="breakdown-item">
                        <div class="breakdown-value">$${(annualSavings * 5).toFixed(0)}</div>
                        <div class="breakdown-label">5 Years</div>
                    </div>
                    <div class="breakdown-item">
                        <div class="breakdown-value">$${opportunityCost.toFixed(2)}</div>
                        <div class="breakdown-label">Current Loss</div>
                    </div>
                </div>
            </div>
        `;
    }

    createSourceSection(data) {
        // Check for data source from recommendation or market analysis
        let source = 'AI Analysis';
        let sourceUrl = null;
        
        if (data.recommendation?.best_overall?.data_source) {
            source = data.recommendation.best_overall.data_source;
            if (source.startsWith('http')) {
                sourceUrl = source;
                source = 'Live Market Data';
            } else if (source.includes('FALLBACK')) {
                source = 'Cached Data (Demo Mode)';
            }
        } else if (data.market_analysis?.results?.length > 0) {
            source = 'Live Market Data';
            sourceUrl = data.market_analysis.results[0].url;
        }
        
        const isLive = !source.toLowerCase().includes('fallback') && !source.toLowerCase().includes('cached');
        
        return `
            <div class="source-info">
                <div class="source-icon">${isLive ? '🟢' : '🟡'}</div>
                <div class="source-text">
                    Data Source: <span class="source-type">${source}</span>
                    ${sourceUrl ? `<a href="${sourceUrl}" target="_blank" style="margin-left: 10px; color: var(--accent-green);">View Source →</a>` : ''}
                </div>
            </div>
        `;
    }

    calculateConfidence(data) {
        // Check multiple sources for confidence calculation
        const hasMarketData = data.market_analysis?.results?.length > 0;
        const hasRecommendation = data.recommendation?.best_overall;
        const dataSource = data.recommendation?.best_overall?.data_source || '';
        
        if (hasMarketData && hasRecommendation && !dataSource.includes('FALLBACK')) {
            return 95;
        } else if (hasRecommendation && !dataSource.includes('FALLBACK')) {
            return 90;
        } else if (dataSource.includes('FALLBACK')) {
            return 75;
        }
        return 85;
    }

    animateResults() {
        const elements = this.results.querySelectorAll('.metric-card, .transaction-card, .card-recommendation, .impact-section');
        elements.forEach((el, index) => {
            setTimeout(() => {
                el.classList.add('slide-in');
            }, index * 100);
        });
    }

    showError(message) {
        this.results.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${message}
            </div>
        `;
        this.results.classList.add('active');
    }

    // --- Premium layout rendering (migrated from inline script) ---
    renderRecommendations(data) {
        const container = this.results;
        if (!container) return;

        const recommendation = data.recommendation || {};
        const transaction = data.parsed_transaction || data.transaction || {};
        const impact = data.financial_impact || {};

        let html = '';

        // Transaction Analysis Section
        html += `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin-bottom: 30px;">
                <h3 style="color: #10b981; margin: 0 0 20px 0; font-size: 1.3rem;">📊 Transaction Analysis</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px;">
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 4px;">Merchant</div>
                        <div style="color: #e2e8f0; font-size: 1.1rem; font-weight: 500;">${transaction.merchant || 'Unknown'}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 4px;">Amount</div>
                        <div style="color: #e2e8f0; font-size: 1.1rem; font-weight: 500;">$${Number(transaction.amount || 0).toFixed(2)}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 4px;">Category</div>
                        <div style="color: #e2e8f0; font-size: 1.1rem; font-weight: 500;">${this.capitalize(transaction.category || 'Other')}</div>
                    </div>
                </div>
            </div>
        `;

        // Recommended Cards Section
        html += '<div style="margin-bottom: 30px;"><h3 style="color: #e2e8f0; margin: 0 0 20px 0; font-size: 1.3rem;">🎯 Recommended Cards</h3>';

        if (recommendation.best_overall) {
            // Contextual note when best has no fee but slightly lower headline rewards than runner up
            const ru = recommendation.runner_up || {};
            const best = recommendation.best_overall || {};
            const bestAmt = Number(best.reward_amount || best.reward_value || 0);
            const ruAmt = Number(ru.reward_amount || ru.reward_value || 0);
            const noteHtml = ((best.annual_fee || 0) === 0 && (ru.annual_fee || 0) > 0 && bestAmt < ruAmt)
                ? `
                <div style="margin-top: 12px; padding: 10px 12px; border-left: 3px solid #10b981; background: rgba(16,185,129,0.08); border-radius: 8px; color: #cbd5e1;">
                    <strong style="color:#10b981;">Why this pick:</strong> We prioritized <em>no annual fee</em> with solid rewards. If you plan to spend heavily in ${this.capitalize(transaction.category || 'this')} over time, consider <strong>${ru.name || 'the runner-up card'}</strong> for a higher headline rate, but note its annual fee.
                </div>
                `
                : '';
            html += this.createModernCardHtml(recommendation.best_overall, true, noteHtml, Number(transaction.amount || 0));
        }
        if (recommendation.runner_up) {
            html += this.createModernCardHtml(recommendation.runner_up, false, '', Number(transaction.amount || 0));
        }
        if (recommendation.alternative) {
            html += this.createModernCardHtml(recommendation.alternative, false, '', Number(transaction.amount || 0));
        }

        html += '</div>';

        // Smart Insights Section
        const bestCard = recommendation.best_overall || {};
        const rewardAmount = bestCard.reward_amount || bestCard.reward_value || 0;
        const transactionAmount = Number(transaction.amount || 100);
        const basicCardReward = transactionAmount * this.getBaselineRate();
        const additionalReward = Number(rewardAmount) - basicCardReward;

        html += `
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(6, 182, 212, 0.05)); border: 1px solid rgba(16, 185, 129, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                <h3 style="color: #10b981; margin: 0 0 20px 0; font-size: 1.3rem;">🔎 Smart Insights</h3>
                <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #e2e8f0; font-weight: 500;">Per purchase vs. 2% baseline</span>
                        <span style="color: #10b981; font-weight: 600; font-size: 1.05rem;">+$${Math.max(Number(additionalReward), 0).toFixed(2)}</span>
                    </div>
                </div>
                <div style="color: #94a3b8; font-size: 0.92rem;">Best for <strong>${this.capitalize(transaction.category || 'this')}</strong> purchases with ${bestCard.reward_rate || 'enhanced'} rewards${bestCard.signup_bonus ? ` and signup bonus: <strong>${bestCard.signup_bonus}</strong>` : ''}.</div>
            </div>
        `;

        // Savings Projection with adjustable frequency
        html += this.createSavingsProjection(data);

        // Append data source attribution
        html += this.createSourceSection(data);

        container.innerHTML = html;
        // Attach handlers for savings control after rendering
        this.attachSavingsProjectionHandlers(data);
        // Ensure results section is visible after rendering
        container.classList.add('active');
        this.animateResults();
    }

    createModernCardHtml(card, isBest, extraHtml = '', txnAmount = 0) {
        const name = card.name || card.card_name || 'Unknown Card';
        const rewardAmount = card.reward_amount || card.reward_value || 0;
        const rewardRate = card.reward_rate || (txnAmount > 0 && Number(rewardAmount) > 0 ? `${((Number(rewardAmount) / txnAmount) * 100).toFixed(1)}% cash back` : '—');
        const fee = card.annual_fee || 0;

        return `
            <div style="background: ${isBest ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 182, 212, 0.1))' : 'rgba(255,255,255,0.03)'}; 
                       border: 1px solid ${isBest ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255,255,255, 0.1)'}; 
                       padding: 20px; border-radius: 12px; margin-bottom: 15px;">
                ${isBest ? '<div style="display: inline-block; background: linear-gradient(135deg, #10b981, #06b6d4); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 10px; font-weight: 600;">BEST MATCH</div>' : ''}
                <h4 style="color: #e2e8f0; margin: 0 0 10px 0; font-size: 1.2rem;">${name}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 4px;">Reward Rate</div>
                        <div style="color: #10b981; font-size: 1.1rem; font-weight: 600;">${rewardRate}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 4px;">Cash Back</div>
                        <div style="color: #10b981; font-size: 1.1rem; font-weight: 600;">+$${Number(rewardAmount).toFixed(2)}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 4px;">Annual Fee</div>
                        <div style="color: #e2e8f0; font-size: 1rem;">${fee === 0 ? 'No Fee' : '$' + fee}</div>
                    </div>
                </div>
                ${card.signup_bonus ? `<div style="margin-top: 15px; padding: 10px; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border-left: 3px solid #10b981;"><strong style=\"color: #10b981;\">Bonus:</strong> <span style=\"color: #e2e8f0;\">${card.signup_bonus}</span></div>` : ''}
                ${card.ai_reasoning ? `<div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid #64748b;"><strong style=\"color: #94a3b8;\">Why this card:</strong> <span style=\"color: #cbd5e1;\">${card.ai_reasoning}</span></div>` : ''}
                ${extraHtml}
            </div>
        `;
    }

    createSavingsProjection(data) {
        const recommendation = data.recommendation || {};
        const transaction = data.parsed_transaction || data.transaction || {};
        const best = recommendation.best_overall || {};
        const amount = Number(transaction.amount || 0);
        const perPurchaseBest = Number(best.reward_amount || best.reward_value || 0);
        const perPurchaseBaseline = amount * this.getBaselineRate();
        const extraPerPurchase = Math.max(perPurchaseBest - perPurchaseBaseline, 0);
        const category = transaction.category || 'General';
        const saved = this.loadFrequencyPref(category);
        const preset = saved || this.getFrequencyPresetForCategory(category);
        const factor = this.periodFactor(preset.period);
        const perYear = preset.value * factor;
        const annualExtra = extraPerPurchase * perYear;
        const annualBest = perPurchaseBest * perYear;
        const annualBaseline = perPurchaseBaseline * perYear;
        const unitLabel = this.formatFrequencyLabel(preset.period, category);

        return `
            <div id="savingsProjection" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                <h3 style="color: #e2e8f0; margin: 0 0 12px 0; font-size: 1.2rem;">📅 Annual Savings</h3>
                <div style="display:flex; gap:12px; align-items:center; flex-wrap: wrap; margin-bottom: 14px;">
                    <span style="color:#94a3b8;">Usage:</span>
                    <input id="freqValue" type="number" min="0" step="1" value="${preset.value}" style="width:90px; padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.04); color:#e2e8f0;" />
                    <select id="freqPeriod" style="padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.04); color:#e2e8f0;">
                        <option value="per_week" ${preset.period==='per_week'?'selected':''}>per week</option>
                        <option value="per_month" ${preset.period==='per_month'?'selected':''}>per month</option>
                        <option value="per_year" ${preset.period==='per_year'?'selected':''}>per year</option>
                        <option value="per_trip" ${preset.period==='per_trip'?'selected':''}>trips per year</option>
                    </select>
                    <label style="display:flex; align-items:center; gap:6px; color:#94a3b8;">
                        <input id="freqSave" type="checkbox" /> Save as default for ${this.capitalize(category)}
                    </label>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px;">
                    <div style="background: rgba(16,185,129,0.08); padding: 12px; border-radius: 10px; border-left: 3px solid #10b981;">
                        <div style="color:#94a3b8; font-size: 0.8rem;">Extra vs. 2% baseline</div>
                        <div class="val-extra" style="color:#10b981; font-weight:700; font-size: 1.2rem;">$${annualExtra.toFixed(2)}</div>
                    </div>
                    <div style="background: rgba(6,182,212,0.08); padding: 12px; border-radius: 10px; border-left: 3px solid #06b6d4;">
                        <div style="color:#94a3b8; font-size: 0.8rem;">With recommended card</div>
                        <div class="val-best" style="color:#e2e8f0; font-weight:700; font-size: 1.2rem;">$${annualBest.toFixed(2)}</div>
                    </div>
                    <div style="background: rgba(148,163,184,0.08); padding: 12px; border-radius: 10px; border-left: 3px solid #64748b;">
                        <div style="color:#94a3b8; font-size: 0.8rem;">With 2% baseline</div>
                        <div class="val-baseline" style="color:#e2e8f0; font-weight:700; font-size: 1.2rem;">$${annualBaseline.toFixed(2)}</div>
                    </div>
                </div>
                <div class="assumption-text" style="color:#94a3b8; font-size: 0.9rem; margin-top: 8px;">Assumes typical purchase of $${amount.toFixed(2)} × ${preset.value} ${unitLabel}.</div>
                <div style="display:none" data-amount="${amount}" data-best="${perPurchaseBest}" data-baseline="${perPurchaseBaseline}" data-category="${this.capitalize(category)}"></div>
            </div>
        `;
    }

    attachSavingsProjectionHandlers(data) {
        const container = document.getElementById('savingsProjection');
        if (!container) return;
        const hidden = container.querySelector('[data-amount]');
        if (!hidden) return;
        const amount = Number(hidden.getAttribute('data-amount')) || 0;
        const perPurchaseBest = Number(hidden.getAttribute('data-best')) || 0;
        const perPurchaseBaseline = Number(hidden.getAttribute('data-baseline')) || 0;
        const category = hidden.getAttribute('data-category') || 'General';
        const valueEl = container.querySelector('#freqValue');
        const periodEl = container.querySelector('#freqPeriod');
        const saveEl = container.querySelector('#freqSave');
        const extraEl = container.querySelector('.val-extra');
        const bestEl = container.querySelector('.val-best');
        const baseEl = container.querySelector('.val-baseline');
        const assumeEl = container.querySelector('.assumption-text');

        const recompute = () => {
            const value = Math.max(Number(valueEl.value || 0), 0);
            const period = periodEl.value;
            const perYear = value * this.periodFactor(period);
            const annualExtra = Math.max(perPurchaseBest - perPurchaseBaseline, 0) * perYear;
            const annualBest = perPurchaseBest * perYear;
            const annualBaseline = perPurchaseBaseline * perYear;
            extraEl.textContent = `$${annualExtra.toFixed(2)}`;
            bestEl.textContent = `$${annualBest.toFixed(2)}`;
            baseEl.textContent = `$${annualBaseline.toFixed(2)}`;
            assumeEl.textContent = `Assumes typical purchase of $${amount.toFixed(2)} × ${value} ${this.formatFrequencyLabel(period, category)}.`;
        };

        valueEl.addEventListener('input', recompute);
        periodEl.addEventListener('change', recompute);
        saveEl.addEventListener('change', () => {
            if (saveEl.checked) {
                const value = Math.max(Number(valueEl.value || 0), 0);
                const period = periodEl.value;
                this.saveFrequencyPref(category, value, period);
            }
        });
    }

    runDemo(scenario) {
        if (!scenario || !this.demoScenarios[scenario]) return;
        if (!this.queryInput) return;
        this.queryInput.value = this.demoScenarios[scenario];
        this.queryInput.focus();
        this.analyzeTransaction();
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.switcherInstance = new Switcher();
    });
} else {
    window.switcherInstance = new Switcher();
}
