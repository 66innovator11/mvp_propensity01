/**
 * API Service for cluster analysis application
 * Handles all backend communication for cluster operations
 */

const API_BASE_URL = 'http://localhost:5000';

export interface Customer {
  customer_id: string;
  name: string;
  address: string;
  propensity_score: number;
  insurance_product: string;
  existing_products: string[];
  age: number;
  annual_income: string;
  email: string;
  phone: string;
  cluster_id: number;
  risk_profile: string;
  last_contact: string;
}

export interface ClusterDetailsResponse {
  status: string;
  product_name: string;
  total_customers: number;
  customers: Customer[];
}

export interface PipelineResponse {
  status: string;
  message: string;
  cluster_results: any[];
  total_products_analyzed: number;
  execution_time: string;
}

export interface EmailDraft {
  customer_id: string;
  customer_name: string;
  product_name: string;
  subject: string;
  email_content: string;
  propensity_score: number;
  agent_name: string;
  agent_contact: string;
  generated_date: string;
  sent_date?: string;
  status: string;
}

export interface SendEmailsResponse {
  status: string;
  message: string;
  product_name: string;
  total_emails: number;
  emails_prepared: boolean;
}

export interface ReviewEmailsResponse {
  status: string;
  total_emails: number;
  emails: EmailDraft[];
}

class ApiService {
  /**
   * Upload files to Google Cloud Storage
   */
  async uploadFiles(files: FileList): Promise<any> {
    const formData = new FormData();
    
    // Add all files to FormData
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Upload failed');
    }

    return response.json();
  }

  /**
   * Run the propensity analysis pipeline
   */
  async runPipeline(): Promise<PipelineResponse> {
    const response = await fetch(`${API_BASE_URL}/run-pipeline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Pipeline execution failed');
    }

    return response.json();
  }

  /**
   * Get cluster details for a specific product
   */
  async getClusterDetails(productName: string): Promise<ClusterDetailsResponse> {
    const response = await fetch(`${API_BASE_URL}/cluster-details/${productName}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch cluster details');
    }

    return response.json();
  }

  /**
   * Test backend connectivity
   */
  async testConnectivity(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/test`, {
      method: 'GET',
      mode: 'cors',
    });

    if (!response.ok) {
      throw new Error('Backend connectivity failed');
    }

    return response.json();
  }

  /**
   * Check backend health
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }

  /**
   * Send emails for a specific product
   */
  async sendEmails(productName: string): Promise<SendEmailsResponse> {
    const response = await fetch(`${API_BASE_URL}/send-emails/${productName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send emails');
    }

    return response.json();
  }

  /**
   * Get all draft emails for review
   */
  async reviewEmails(): Promise<ReviewEmailsResponse> {
    const response = await fetch(`${API_BASE_URL}/review-emails`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch emails for review');
    }

    return response.json();
  }

  /**
   * Finalize and send all emails
   */
  async finalizeEmails(): Promise<ReviewEmailsResponse> {
    // Use GET method since review-emails only accepts GET
    const response = await fetch(`${API_BASE_URL}/review-emails`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send emails');
    }

    const result = await response.json();
    
    // Update all emails to "Email Sent" status
    const updatedEmails = result.emails.map((email: any) => ({
      ...email,
      status: 'Email Sent',
      sent_date: new Date().toISOString()
    }));

    return {
      ...result,
      emails: updatedEmails
    };
  }
}

// Export singleton instance
export const apiService = new ApiService();
