#!/usr/bin/env python3
import unittest
from tick_calc import TicketSalesCalculator

class TestTicketSalesCalculator(unittest.TestCase):
    def setUp(self):
        """Set up a calculator instance with sample data for each test"""
        self.calculator = TicketSalesCalculator(
            desired_total_value=1000000,
            total_participants=80000,
            cost_per_participant=750,
            non_paying_lower=20000,
            non_paying_upper=30000,
            tiers=[550, 750, 1000, 1250],
            allocation_percentages=[40, 30, 20, 10],
            first_batch_total=20000,
            num_batches=4
        )

    def test_initialization(self):
        """Test that calculator initializes with correct values"""
        self.assertEqual(self.calculator.desired_total_value, 1000000)
        self.assertEqual(self.calculator.total_participants, 80000)
        self.assertEqual(self.calculator.tiers, [550, 750, 1000, 1250])
        self.assertEqual(self.calculator.allocation_percentages, [40, 30, 20, 10])
        self.assertEqual(self.calculator.global_ticket_cap, 80000)

    def test_non_paying_calculations(self):
        """Test calculations related to non-paying participants"""
        self.assertEqual(self.calculator.non_paying_mid, 25000)
        self.assertEqual(self.calculator.paying_best, 50000)  # 80000 - 30000
        self.assertEqual(self.calculator.paying_worst, 60000)  # 80000 - 20000
        self.assertEqual(self.calculator.paying_mid, 55000)  # 80000 - 25000

    def test_initial_allocations(self):
        """Test that initial batch allocations are calculated correctly"""
        expected_allocations = [8000, 6000, 4000, 2000]  # 40%, 30%, 20%, 10% of 20000
        self.assertEqual(self.calculator.current_batch_planned_allocations, expected_allocations)

    def test_add_batch(self):
        """Test adding a batch of sales"""
        test_sales = [7500, 6000, 4500, 2000]
        self.calculator.add_batch(test_sales)
        
        # Test cumulative sales
        self.assertEqual(self.calculator.cumulative_sales, test_sales)
        
        # Test revenue calculation
        expected_revenue = (
            7500 * 550 +  # Tier 1
            6000 * 750 +  # Tier 2
            4500 * 1000 + # Tier 3
            2000 * 1250   # Tier 4
        )
        self.assertEqual(self.calculator.cumulative_revenue, expected_revenue)

    def test_remaining_calculations(self):
        """Test remaining tickets and revenue calculations"""
        # Add a batch of sales first
        test_sales = [7500, 6000, 4500, 2000]
        self.calculator.add_batch(test_sales)
        
        # Test remaining tickets
        total_sold = sum(test_sales)
        expected_remaining = self.calculator.global_ticket_cap - total_sold
        self.assertEqual(self.calculator.remaining_tickets_global(), expected_remaining)
        
        # Test remaining revenue
        expected_remaining_revenue = self.calculator.revenue_target - self.calculator.cumulative_revenue
        self.assertEqual(self.calculator.remaining_revenue(), expected_remaining_revenue)

    def test_multiple_batches(self):
        """Test handling multiple batches of sales"""
        batch1 = [7500, 6000, 4500, 2000]
        batch2 = [8000, 5500, 4000, 2500]
        
        self.calculator.add_batch(batch1)
        self.calculator.add_batch(batch2)
        
        # Test cumulative sales
        expected_sales = [
            batch1[0] + batch2[0],
            batch1[1] + batch2[1],
            batch1[2] + batch2[2],
            batch1[3] + batch2[3]
        ]
        self.assertEqual(self.calculator.cumulative_sales, expected_sales)
        
        # Test number of recorded batches
        self.assertEqual(len(self.calculator.batches), 2)

    def test_revenue_target_validation(self):
        """Test revenue calculations against the target"""
        # The revenue target should be based on paying_mid * cost_per_participant
        expected_target = self.calculator.paying_mid * self.calculator.cost_per_participant
        self.assertEqual(self.calculator.revenue_target, expected_target)

if __name__ == '__main__':
    unittest.main()
