# System surfaces and accessibility

Read this for SpringBoard, system prompts, hardware input, Widget Gallery, Control Center, or accessibility configuration.

Use the exact UDID and current display/accessibility state. Resolve a target by semantic properties and current geometry, perform one interaction, then observe the resulting state. Preserve any connection continuity required by the upstream `serve-sim` skill for multi-step gestures.

For an accessibility matrix, change one required dimension at a time—device size, appearance, Dynamic Type, VoiceOver, Reduce Motion, keyboard, or permission state. Assert the configuration before observing product behavior, and restore every changed setting during cleanup.

Do not boot additional runtimes merely as a speculative recovery step.
