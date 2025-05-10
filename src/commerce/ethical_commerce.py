#!/usr/bin/env python3
"""
Ethical Commerce Manager for SoulCoreHub
Manages affiliate products, own products, and e-commerce integrations
"""

import os
import json
import uuid
import logging
import datetime
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EthicalCommerce')

class EthicalCommerceManager:
    """
    Manages ethical commerce operations for SoulCoreHub
    Handles affiliate products, own products, and e-commerce integrations
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize the Ethical Commerce Manager
        
        Args:
            data_dir (str, optional): Directory for commerce data
        """
        if data_dir is None:
            data_dir = "data/commerce"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.affiliate_products_file = self.data_dir / "vetted_affiliate_products.csv"
        self.own_products_file = self.data_dir / "own_products.csv"
        self.sales_data_file = self.data_dir / "sales_data.csv"
        
        # Load data
        self.affiliate_products = self._load_affiliate_products()
        self.own_products = self._load_own_products()
        self.sales_data = self._load_sales_data()
        
        logger.info("Ethical Commerce Manager initialized")
    
    def _load_affiliate_products(self):
        """
        Load vetted affiliate products
        
        Returns:
            list: List of affiliate products
        """
        try:
            if self.affiliate_products_file.exists():
                df = pd.read_csv(self.affiliate_products_file)
                logger.info(f"Loaded {len(df)} affiliate products")
                return df.to_dict('records')
            else:
                # Create empty file with structure
                columns = [
                    'id', 'name', 'description', 'category', 'vendor', 'price', 
                    'affiliate_link', 'commission_rate', 'verified', 
                    'verification_date', 'verification_notes', 'rating', 
                    'pros', 'cons', 'tags'
                ]
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.affiliate_products_file, index=False)
                logger.info("Created new affiliate products file")
                return []
        except Exception as e:
            logger.error(f"Failed to load affiliate products: {str(e)}")
            return []
    
    def _load_own_products(self):
        """
        Load own products
        
        Returns:
            list: List of own products
        """
        try:
            if self.own_products_file.exists():
                df = pd.read_csv(self.own_products_file)
                logger.info(f"Loaded {len(df)} own products")
                return df.to_dict('records')
            else:
                # Create empty file with structure
                columns = [
                    'id', 'name', 'description', 'category', 'price', 
                    'cost', 'inventory', 'sku', 'created_date', 
                    'last_updated', 'shopify_id', 'amazon_asin', 
                    'image_url', 'product_url', 'tags'
                ]
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.own_products_file, index=False)
                logger.info("Created new own products file")
                return []
        except Exception as e:
            logger.error(f"Failed to load own products: {str(e)}")
            return []
    
    def _load_sales_data(self):
        """
        Load sales data
        
        Returns:
            list: List of sales records
        """
        try:
            if self.sales_data_file.exists():
                df = pd.read_csv(self.sales_data_file)
                logger.info(f"Loaded {len(df)} sales records")
                return df.to_dict('records')
            else:
                # Create empty file with structure
                columns = [
                    'id', 'date', 'product_id', 'product_type', 'quantity', 
                    'price', 'revenue', 'cost', 'profit', 'platform', 
                    'customer_id', 'order_id', 'affiliate_id'
                ]
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.sales_data_file, index=False)
                logger.info("Created new sales data file")
                return []
        except Exception as e:
            logger.error(f"Failed to load sales data: {str(e)}")
            return []
    
    def add_vetted_product(self, product_data, verification_notes):
        """
        Add a new vetted affiliate product
        
        Args:
            product_data (dict): Product data
            verification_notes (str): Notes on product verification
            
        Returns:
            dict: Result of operation
        """
        try:
            # Validate required fields
            required_fields = ['name', 'description', 'category', 'vendor', 'price', 'affiliate_link']
            for field in required_fields:
                if field not in product_data:
                    return {
                        "success": False, 
                        "error": f"Missing required field: {field}"
                    }
            
            # Ensure verification notes are substantial
            if not verification_notes or len(verification_notes) < 50:
                return {
                    "success": False, 
                    "error": "Insufficient verification notes. Please provide detailed verification information."
                }
            
            # Generate ID if not provided
            if 'id' not in product_data:
                product_data['id'] = str(uuid.uuid4())
            
            # Add verification metadata
            product_data['verified'] = True
            product_data['verification_date'] = datetime.datetime.now().isoformat()
            product_data['verification_notes'] = verification_notes
            
            # Add to dataframe and save
            df = pd.DataFrame(self.affiliate_products)
            df = pd.concat([df, pd.DataFrame([product_data])], ignore_index=True)
            df.to_csv(self.affiliate_products_file, index=False)
            
            # Update in-memory list
            self.affiliate_products = df.to_dict('records')
            
            logger.info(f"Added new affiliate product: {product_data['name']}")
            return {
                "success": True, 
                "product_id": product_data['id']
            }
        except Exception as e:
            logger.error(f"Failed to add affiliate product: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def add_own_product(self, product_data):
        """
        Add a new own product
        
        Args:
            product_data (dict): Product data
            
        Returns:
            dict: Result of operation
        """
        try:
            # Validate required fields
            required_fields = ['name', 'description', 'category', 'price']
            for field in required_fields:
                if field not in product_data:
                    return {
                        "success": False, 
                        "error": f"Missing required field: {field}"
                    }
            
            # Generate ID if not provided
            if 'id' not in product_data:
                product_data['id'] = str(uuid.uuid4())
            
            # Add metadata
            product_data['created_date'] = datetime.datetime.now().isoformat()
            product_data['last_updated'] = datetime.datetime.now().isoformat()
            
            # Add to dataframe and save
            df = pd.DataFrame(self.own_products)
            df = pd.concat([df, pd.DataFrame([product_data])], ignore_index=True)
            df.to_csv(self.own_products_file, index=False)
            
            # Update in-memory list
            self.own_products = df.to_dict('records')
            
            logger.info(f"Added new own product: {product_data['name']}")
            return {
                "success": True, 
                "product_id": product_data['id']
            }
        except Exception as e:
            logger.error(f"Failed to add own product: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def record_sale(self, sale_data):
        """
        Record a sale
        
        Args:
            sale_data (dict): Sale data
            
        Returns:
            dict: Result of operation
        """
        try:
            # Validate required fields
            required_fields = ['product_id', 'product_type', 'quantity', 'price']
            for field in required_fields:
                if field not in sale_data:
                    return {
                        "success": False, 
                        "error": f"Missing required field: {field}"
                    }
            
            # Generate ID if not provided
            if 'id' not in sale_data:
                sale_data['id'] = str(uuid.uuid4())
            
            # Add date if not provided
            if 'date' not in sale_data:
                sale_data['date'] = datetime.datetime.now().isoformat()
            
            # Calculate revenue
            if 'revenue' not in sale_data:
                sale_data['revenue'] = float(sale_data['price']) * float(sale_data['quantity'])
            
            # Add to dataframe and save
            df = pd.DataFrame(self.sales_data)
            df = pd.concat([df, pd.DataFrame([sale_data])], ignore_index=True)
            df.to_csv(self.sales_data_file, index=False)
            
            # Update in-memory list
            self.sales_data = df.to_dict('records')
            
            logger.info(f"Recorded new sale: {sale_data['product_id']}")
            return {
                "success": True, 
                "sale_id": sale_data['id']
            }
        except Exception as e:
            logger.error(f"Failed to record sale: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def get_product(self, product_id, product_type='affiliate'):
        """
        Get a product by ID
        
        Args:
            product_id (str): Product ID
            product_type (str): Product type ('affiliate' or 'own')
            
        Returns:
            dict: Product data or None if not found
        """
        products = self.affiliate_products if product_type == 'affiliate' else self.own_products
        
        for product in products:
            if product['id'] == product_id:
                return product
        
        return None
    
    def update_product(self, product_id, product_data, product_type='affiliate'):
        """
        Update a product
        
        Args:
            product_id (str): Product ID
            product_data (dict): Updated product data
            product_type (str): Product type ('affiliate' or 'own')
            
        Returns:
            dict: Result of operation
        """
        try:
            # Determine which product list and file to use
            if product_type == 'affiliate':
                products = self.affiliate_products
                products_file = self.affiliate_products_file
            else:
                products = self.own_products
                products_file = self.own_products_file
                # Update last_updated timestamp for own products
                product_data['last_updated'] = datetime.datetime.now().isoformat()
            
            # Find product index
            product_index = None
            for i, product in enumerate(products):
                if product['id'] == product_id:
                    product_index = i
                    break
            
            if product_index is None:
                return {
                    "success": False, 
                    "error": f"Product with ID {product_id} not found"
                }
            
            # Update product
            updated_product = {**products[product_index], **product_data}
            products[product_index] = updated_product
            
            # Save to file
            df = pd.DataFrame(products)
            df.to_csv(products_file, index=False)
            
            logger.info(f"Updated {product_type} product: {product_id}")
            return {
                "success": True, 
                "product": updated_product
            }
        except Exception as e:
            logger.error(f"Failed to update product: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def delete_product(self, product_id, product_type='affiliate'):
        """
        Delete a product
        
        Args:
            product_id (str): Product ID
            product_type (str): Product type ('affiliate' or 'own')
            
        Returns:
            dict: Result of operation
        """
        try:
            # Determine which product list and file to use
            if product_type == 'affiliate':
                products = self.affiliate_products
                products_file = self.affiliate_products_file
            else:
                products = self.own_products
                products_file = self.own_products_file
            
            # Find product index
            product_index = None
            for i, product in enumerate(products):
                if product['id'] == product_id:
                    product_index = i
                    break
            
            if product_index is None:
                return {
                    "success": False, 
                    "error": f"Product with ID {product_id} not found"
                }
            
            # Remove product
            removed_product = products.pop(product_index)
            
            # Save to file
            df = pd.DataFrame(products)
            df.to_csv(products_file, index=False)
            
            # Update in-memory list
            if product_type == 'affiliate':
                self.affiliate_products = products
            else:
                self.own_products = products
            
            logger.info(f"Deleted {product_type} product: {product_id}")
            return {
                "success": True, 
                "product": removed_product
            }
        except Exception as e:
            logger.error(f"Failed to delete product: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def get_sales_report(self, start_date=None, end_date=None, product_type=None):
        """
        Get sales report
        
        Args:
            start_date (str, optional): Start date (ISO format)
            end_date (str, optional): End date (ISO format)
            product_type (str, optional): Product type filter
            
        Returns:
            dict: Sales report
        """
        try:
            # Convert to DataFrame for easier filtering and aggregation
            df = pd.DataFrame(self.sales_data)
            
            if len(df) == 0:
                return {
                    "success": True,
                    "total_sales": 0,
                    "total_revenue": 0,
                    "total_profit": 0,
                    "sales_by_product": [],
                    "sales_by_date": []
                }
            
            # Apply filters
            if start_date:
                df = df[df['date'] >= start_date]
            
            if end_date:
                df = df[df['date'] <= end_date]
            
            if product_type:
                df = df[df['product_type'] == product_type]
            
            # Calculate totals
            total_sales = len(df)
            total_revenue = df['revenue'].sum() if 'revenue' in df.columns and not df['revenue'].empty else 0
            total_profit = df['profit'].sum() if 'profit' in df.columns and not df['profit'].empty else 0
            
            # Group by product
            sales_by_product = []
            if 'product_id' in df.columns and not df.empty:
                product_groups = df.groupby('product_id').agg({
                    'quantity': 'sum',
                    'revenue': 'sum',
                    'profit': 'sum' if 'profit' in df.columns else None
                }).reset_index()
                
                sales_by_product = product_groups.to_dict('records')
            
            # Group by date
            sales_by_date = []
            if 'date' in df.columns and not df.empty:
                # Extract date part only
                df['date_only'] = pd.to_datetime(df['date']).dt.date
                
                date_groups = df.groupby('date_only').agg({
                    'quantity': 'sum',
                    'revenue': 'sum',
                    'profit': 'sum' if 'profit' in df.columns else None
                }).reset_index()
                
                sales_by_date = date_groups.to_dict('records')
            
            return {
                "success": True,
                "total_sales": total_sales,
                "total_revenue": float(total_revenue),
                "total_profit": float(total_profit),
                "sales_by_product": sales_by_product,
                "sales_by_date": sales_by_date
            }
        except Exception as e:
            logger.error(f"Failed to generate sales report: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_affiliate_links_csv(self, output_file=None):
        """
        Export affiliate links to CSV
        
        Args:
            output_file (str, optional): Output file path
            
        Returns:
            str: Path to exported file
        """
        try:
            if output_file is None:
                output_file = self.data_dir / "affiliate_links_export.csv"
            
            # Create DataFrame with relevant columns
            df = pd.DataFrame(self.affiliate_products)
            
            if len(df) == 0:
                # Create empty file with structure
                columns = [
                    'name', 'category', 'vendor', 'affiliate_link', 
                    'commission_rate', 'signup_link', 'notes'
                ]
                pd.DataFrame(columns=columns).to_csv(output_file, index=False)
            else:
                # Select and rename columns
                export_df = df[['name', 'category', 'vendor', 'affiliate_link', 'commission_rate']]
                
                # Add empty columns for signup link and notes
                export_df['signup_link'] = ''
                export_df['notes'] = ''
                
                export_df.to_csv(output_file, index=False)
            
            logger.info(f"Exported affiliate links to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to export affiliate links: {str(e)}")
            return None
    
    def import_affiliate_links_csv(self, input_file):
        """
        Import affiliate links from CSV
        
        Args:
            input_file (str): Input file path
            
        Returns:
            dict: Result of operation
        """
        try:
            # Read CSV file
            df = pd.read_csv(input_file)
            
            # Validate required columns
            required_columns = ['name', 'category', 'vendor', 'affiliate_link']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    "success": False,
                    "error": f"Missing required columns: {', '.join(missing_columns)}"
                }
            
            # Process each row
            imported_count = 0
            for _, row in df.iterrows():
                # Create product data
                product_data = {
                    'name': row['name'],
                    'category': row['category'],
                    'vendor': row['vendor'],
                    'affiliate_link': row['affiliate_link'],
                    'commission_rate': row.get('commission_rate', 0),
                    'description': row.get('description', f"Product from {row['vendor']}"),
                    'price': row.get('price', 0),
                    'id': str(uuid.uuid4())
                }
                
                # Get verification notes
                verification_notes = row.get('notes', '')
                if not verification_notes or len(verification_notes) < 50:
                    verification_notes = f"Imported from CSV. Vendor: {row['vendor']}. " \
                                        f"This product was verified as part of a bulk import " \
                                        f"on {datetime.datetime.now().isoformat()}."
                
                # Add product
                result = self.add_vetted_product(product_data, verification_notes)
                
                if result['success']:
                    imported_count += 1
            
            return {
                "success": True,
                "imported_count": imported_count,
                "total_rows": len(df)
            }
        except Exception as e:
            logger.error(f"Failed to import affiliate links: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_affiliate_report(self, output_file=None):
        """
        Generate a markdown report of affiliate products
        
        Args:
            output_file (str, optional): Output file path
            
        Returns:
            str: Path to generated file
        """
        try:
            if output_file is None:
                output_file = self.data_dir / "affiliate_report.md"
            
            with open(output_file, 'w') as f:
                f.write("# SoulCoreHub Affiliate Products Report\n\n")
                f.write(f"Generated on: {datetime.datetime.now().isoformat()}\n\n")
                
                # Group products by category
                df = pd.DataFrame(self.affiliate_products)
                
                if len(df) == 0:
                    f.write("No affiliate products found.\n")
                else:
                    categories = df['category'].unique()
                    
                    for category in categories:
                        f.write(f"## {category}\n\n")
                        
                        category_products = df[df['category'] == category]
                        
                        for _, product in category_products.iterrows():
                            f.write(f"### {product['name']}\n\n")
                            f.write(f"**Vendor:** {product['vendor']}\n\n")
                            f.write(f"**Description:** {product['description']}\n\n")
                            f.write(f"**Commission Rate:** {product['commission_rate']}\n\n")
                            
                            if 'pros' in product and product['pros']:
                                f.write("**Pros:**\n")
                                for pro in str(product['pros']).split(','):
                                    f.write(f"- {pro.strip()}\n")
                                f.write("\n")
                            
                            if 'cons' in product and product['cons']:
                                f.write("**Cons:**\n")
                                for con in str(product['cons']).split(','):
                                    f.write(f"- {con.strip()}\n")
                                f.write("\n")
                            
                            f.write("---\n\n")
            
            logger.info(f"Generated affiliate report at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate affiliate report: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    commerce = EthicalCommerceManager()
    
    # Add a sample affiliate product
    sample_product = {
        'name': 'Sample Product',
        'description': 'This is a sample affiliate product',
        'category': 'Software',
        'vendor': 'Sample Vendor',
        'price': 99.99,
        'affiliate_link': 'https://example.com/affiliate/sample',
        'commission_rate': 0.15,
        'pros': 'Easy to use, Great support, Affordable',
        'cons': 'Limited features in free tier'
    }
    
    verification_notes = """
    This product was personally tested for 2 weeks. The affiliate program is legitimate
    and pays on time. The product delivers on its promises and has good customer support.
    Commission rates are competitive and the product has a 30-day money-back guarantee.
    """
    
    commerce.add_vetted_product(sample_product, verification_notes)
    
    # Generate report
    commerce.generate_affiliate_report()
