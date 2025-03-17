from oso import Oso

oso = Oso()

# Load the policy from the file
oso.load_files(["documents/policy.polar"])
