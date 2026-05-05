# Delegation
## 📌 Overview
This module allows managers to delegate their responsibilities to employees with controlled permissions and time-bound access.
## 🎯 Features
- Multi-stage delegation workflow (Draft → Confirmed → Revoked)
- Role-based access control using security groups
- Delegation types with restricted users
- Automatic employee reassignment to delegated manager
- Scheduled job to validate delegation periods
## 🧩 Models
- Delegation Type: Defines allowed users and assigned groups
- Delegations: Manages delegation process and workflow
- HR Employee (Inherited): Adds delegated manager tracking
## 🖥️ Screenshots
<img width="1917" height="390" alt="image" src="https://github.com/user-attachments/assets/3529c8a2-c014-43e1-8ae9-a88da8fd4de4" />
<br><br>
<img width="1917" height="390" alt="image" src="https://github.com/user-attachments/assets/d4ca0ee4-5db2-4ce9-8e7b-a7d15d6de852" />

## 🔄 Delegation Workflow Behavior
### ✅ On Confirm
When a delegation is confirmed:
- The selected delegation type is applied
- The employee in delegation_to is temporarily assigned as a delegated manager
- All employees under the original manager (delegation_from) are updated:
  - Their delegated_manager field is set to the new delegated employee
- The delegated employee also receives the delegated_manager value
- Security groups defined in the delegation type are assigned to the delegated employee
- The delegation becomes active during the defined date range
### ❌ On Revoke or Defined Date:
When a delegation is revoked:
- The delegation is immediately deactivated
- All affected employees are reverted:
  - delegated_manager field is cleared (or restored to original state)
- The delegated employee loses the assigned groups/permissions
- System returns to the original hierarchy (manager regains full control)

  
