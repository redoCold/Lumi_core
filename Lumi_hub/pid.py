class PID:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp  # Proportional: "How hard to turn/slow down right now"
        self.ki = ki  # Integral: "Fixes small errors that stay over time"
        self.kd = kd  # Derivative: "Predicts the future to stop overshooting"
        self.setpoint = setpoint # The goal (e.g., 50cm from wall)
        
        self.prev_error = 0
        self.integral = 0

    def compute(self, current_value):
        error = self.setpoint - current_value
        self.integral += error
        derivative = error - self.prev_error
        
        # Calculate output
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        self.prev_error = error
        return output