const axios = require('axios');

class EnhancedLegalAgent {
    constructor() {
        this.ollamaUrl = 'http://localhost:11434';
        this.model = 'mistral:7b';  // Using mistral for better quality
        this.contractHistory = new Map(); // Store contracts for editing
        console.log('⚖️ ENHANCED LEGAL AGENT INITIALIZED');
    }

    async processRequest(userInput, sessionId = null) {
        console.log('\n📋 PROCESSING LEGAL REQUEST');
        
        // Check if this is an edit request
        const isEditRequest = userInput.toLowerCase().includes('edit') || 
                              userInput.toLowerCase().includes('change') ||
                              userInput.toLowerCase().includes('update') ||
                              userInput.toLowerCase().includes('modify');
        
        if (isEditRequest && sessionId && this.contractHistory.has(sessionId)) {
            return await this.editContract(userInput, sessionId);
        }
        
        // Generate new contract
        const contract = await this.generateContract(userInput);
        
        // Generate a session ID for future edits
        const newSessionId = Date.now().toString();
        this.contractHistory.set(newSessionId, {
            originalRequest: userInput,
            contract: contract,
            timestamp: new Date().toISOString()
        });
        
        return {
            contract: contract,
            sessionId: newSessionId,
            message: "Contract generated! You can edit it by saying 'Edit the contract to...'"
        };
    }

    async editContract(editRequest, sessionId) {
        const previousData = this.contractHistory.get(sessionId);
        
        const prompt = `You are a legal editor. Modify the existing contract based on the edit request.

ORIGINAL CONTRACT:
${previousData.contract}

EDIT REQUEST: "${editRequest}"

INSTRUCTIONS:
1. Make ONLY the requested changes
2. Keep all other clauses exactly the same
3. Update dates, names, amounts as requested
4. Maintain professional legal formatting
5. Return the COMPLETE modified contract

Modified contract:`;

        try {
            const response = await axios.post(`${this.ollamaUrl}/api/generate`, {
                model: this.model,
                prompt: prompt,
                stream: false,
                options: {
                    temperature: 0.2,
                    num_predict: 4000
                }
            });

            const modifiedContract = response.data.response;
            
            // Update history
            this.contractHistory.set(sessionId, {
                ...previousData,
                contract: modifiedContract,
                lastEdit: new Date().toISOString(),
                editHistory: [...(previousData.editHistory || []), editRequest]
            });

            return {
                contract: modifiedContract,
                sessionId: sessionId,
                message: "Contract updated with your changes!"
            };
        } catch (error) {
            console.error('Edit error:', error);
            throw error;
        }
    }

    async generateContract(userInput) {
        console.log('📝 GENERATING CONTRACT...');

        const currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const prompt = `You are a senior partner at a prestigious law firm. Draft a COMPLETE, PROFESSIONAL legal contract based on this request.

CLIENT REQUEST: "${userInput}"

CURRENT DATE: ${currentDate}

INSTRUCTIONS:
1. Create a FULLY EXECUTABLE legal document
2. Use PROPER legal formatting with numbered sections
3. Include ALL specific details from the request
4. Add ALL standard clauses for this contract type
5. Include proper signature blocks
6. Use the CURRENT DATE as the Effective Date
7. Calculate all other dates based on this current date

FORMAT YOUR RESPONSE AS A PROPER CONTRACT WITH:

--------------------------------------------------------------------
[TITLE OF CONTRACT]

THIS [CONTRACT TYPE] (this "Agreement") is made and entered into on this ${currentDate} (the "Effective Date") by and between:

[PARTY 1 NAME] ("[Party 1 Role]")
and
[PARTY 2 NAME] ("[Party 2 Role]")

RECITALS
WHEREAS, ...
WHEREAS, ...
WHEREAS, ...

NOW, THEREFORE, in consideration of the mutual promises contained herein, the parties agree as follows:

1. DEFINITIONS
   1.1 [Term] means ...
   1.2 [Term] means ...

2. SERVICES AND DELIVERABLES
   [Include all specific terms from the request]

3. COMPENSATION
   [Include fee details]

4. INTELLECTUAL PROPERTY RIGHTS
   [Include ownership terms]

5. CONFIDENTIALITY
   [Include confidentiality terms]

6. TERM AND TERMINATION
   [Include duration and termination]

7. LIMITATION OF LIABILITY
   [Include liability cap]

8. DISPUTE RESOLUTION
   [Include arbitration/mediation]

9. GOVERNING LAW
   [Include governing law]

10. MISCELLANEOUS
    [Include standard boilerplate]

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

[PARTY 1]:
By: _____________________________
Name: ___________________________
Title: __________________________
Date: ___________________________

[PARTY 2]:
By: _____________________________
Name: ___________________________
Title: __________________________
Date: ___________________________

Now, generate the complete contract for: "${userInput}"`;

        try {
            const response = await axios.post(`${this.ollamaUrl}/api/generate`, {
                model: this.model,
                prompt: prompt,
                stream: false,
                options: {
                    temperature: 0.2,
                    num_predict: 5000
                }
            });

            return response.data.response;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }

    getContractHistory(sessionId) {
        return this.contractHistory.get(sessionId);
    }
}

module.exports = EnhancedLegalAgent;