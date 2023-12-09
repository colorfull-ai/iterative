export class BaseClient {
    public static BASE_URL: string = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || '';
  
    public static async fetchData(endpoint: string): Promise<any> {
      try {
        const response = await fetch(`${BaseClient.BASE_URL}${endpoint}`);
  
        if (!response.ok) {
          const responseBody = await response.json();
          throw { status: response.status, body: responseBody }; // throw an error object with the status and body
        }
  
        return response.json();
      } catch (err) {
        console.error(err);
      }
    }
  
    public static async postData(endpoint: string, data?: any): Promise<any> {
      const response = await fetch(`${BaseClient.BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : null,
      });
    
      if (!response.ok) {
        const responseBody = await response.json();
        throw { status: response.status, body: responseBody }; // throw an error object with the status and body
      }
    
      return response.json();
    }
  
    public static async putData(endpoint: string, data?: any): Promise<any> {
      try {
        const response = await fetch(`${BaseClient.BASE_URL}${endpoint}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: data ? JSON.stringify(data) : null,
        });
  
  
        if (!response.ok) {
          const responseBody = await response.json();
          throw { status: response.status, body: responseBody }; // throw an error object with the status and body
        }
  
        return response.json();
      } catch (err) {
        console.log(err);
      }
    }
  
    public static async patchData(endpoint: string, data?: any): Promise<any> {
      try {
        const response = await fetch(`${BaseClient.BASE_URL}${endpoint}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: data ? JSON.stringify(data) : null,
        });
  
  
        if (!response.ok) {
          const responseBody = await response.json();
          throw { status: response.status, body: responseBody }; // throw an error object with the status and body
        }
  
        return response.json();
      } catch (err) {
        console.log(err);
      }
    }
  
    public static async deleteData(endpoint: string): Promise<any> {
      try {
        const response = await fetch(`${BaseClient.BASE_URL}${endpoint}`, {
          method: 'DELETE',
        });
  
  
        if (!response.ok) {
          const responseBody = await response.json();
          throw { status: response.status, body: responseBody }; // throw an error object with the status and body
        }
  
        return response.json();
      } catch (err) {
        console.log(err);
      }
    }
  
    public static createQueryString(params?: Record<string, any>): string {
      if (!params) return '';
      const queryStrings = Object.entries(params)
        .filter(([_, value]) => value !== undefined)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
      return queryStrings ? `?${queryStrings}` : '';
    }
  }
  